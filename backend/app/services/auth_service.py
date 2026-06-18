from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    get_password_hash
)
from app.crud.usuario import crud_usuario
from app.models.usuario import Usuario, Sesion
from app.schemas.auth import LoginRequest, TokenData

class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    async def login(db: AsyncSession, login_data: LoginRequest, ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Login de usuario"""
        # Autenticar usuario
        usuario = await crud_usuario.authenticate(
            db,
            username=login_data.username,
            password=login_data.password
        )
        
        if not usuario:
            raise ValueError("Credenciales inválidas o cuenta bloqueada")
        
        # Cargar rol
        usuario_completo = await crud_usuario.get_with_rol(db, str(usuario.id))
        
        # Crear tokens
        token_data = {
            "sub": str(usuario.id),
            "user_id": str(usuario.id),
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario_completo.rol.nombre if usuario_completo.rol else "user",
            "sucursal_id": str(usuario.sucursal_id) if usuario.sucursal_id else None,
            "empresa_id": str(usuario.empresa_id),
        }
        
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        # Crear sesión
        sesion = Sesion(
            usuario_id=usuario.id,
            token_hash=hashlib.sha256(access_token.encode()).hexdigest(),
            refresh_token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            ip_address=ip,
            user_agent=user_agent[:500] if user_agent else None,
            expira_en=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        db.add(sesion)
        await db.flush()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": usuario_completo
        }
    
    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> Dict[str, Any]:
        """Refrescar token de acceso"""
        try:
            payload = decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise ValueError("Token inválido")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise ValueError("Token inválido")
            
            # Verificar sesión
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            result = await db.execute(
                select(Sesion).where(
                    Sesion.refresh_token_hash == token_hash,
                    Sesion.es_activa == True
                )
            )
            sesion = result.scalar_one_or_none()
            
            if not sesion or sesion.expira_en < datetime.utcnow():
                raise ValueError("Sesión expirada")
            
            # Obtener usuario actualizado
            usuario = await crud_usuario.get_with_rol(db, user_id)
            if not usuario or not usuario.esta_activo:
                raise ValueError("Usuario inactivo")
            
            # Crear nuevos tokens
            token_data = {
                "sub": str(usuario.id),
                "user_id": str(usuario.id),
                "username": usuario.username,
                "email": usuario.email,
                "rol": usuario.rol.nombre if usuario.rol else "user",
                "sucursal_id": str(usuario.sucursal_id) if usuario.sucursal_id else None,
                "empresa_id": str(usuario.empresa_id),
            }
            
            new_access_token = create_access_token(data=token_data)
            new_refresh_token = create_refresh_token(data=token_data)
            
            # Actualizar sesión
            sesion.token_hash = hashlib.sha256(new_access_token.encode()).hexdigest()
            sesion.refresh_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
            sesion.ultima_actividad = datetime.utcnow()
            await db.flush()
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        
        except JWTError:
            raise ValueError("Token inválido")
    
    @staticmethod
    async def logout(db: AsyncSession, token: str) -> bool:
        """Cerrar sesión"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        result = await db.execute(
            select(Sesion).where(Sesion.token_hash == token_hash)
        )
        sesion = result.scalar_one_or_none()
        
        if sesion:
            sesion.es_activa = False
            await db.flush()
            return True
        return False
    
    @staticmethod
    async def logout_all_devices(db: AsyncSession, user_id: str) -> int:
        """Cerrar sesión en todos los dispositivos"""
        from uuid import UUID
        from sqlalchemy import update
        
        result = await db.execute(
            update(Sesion)
            .where(Sesion.usuario_id == UUID(user_id))
            .values(es_activa=False)
        )
        await db.flush()
        return result.rowcount
    
    @staticmethod
    async def get_current_user(db: AsyncSession, token: str) -> Usuario:
        """Obtener usuario actual del token"""
        try:
            payload = decode_token(token)
            if not payload or payload.get("type") != "access":
                raise ValueError("Token inválido")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise ValueError("Token inválido")
            
            # Verificar sesión activa
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            result = await db.execute(
                select(Sesion).where(
                    Sesion.token_hash == token_hash,
                    Sesion.es_activa == True
                )
            )
            sesion = result.scalar_one_or_none()
            
            if not sesion:
                raise ValueError("Sesión no válida")
            
            # Actualizar última actividad
            sesion.ultima_actividad = datetime.utcnow()
            
            # Obtener usuario
            usuario = await crud_usuario.get_with_rol(db, user_id)
            if not usuario:
                raise ValueError("Usuario no encontrado")
            
            if not usuario.esta_activo:
                raise ValueError("Usuario inactivo")
            
            await db.flush()
            return usuario
        
        except JWTError:
            raise ValueError("Token inválido")
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        usuario: Usuario,
        password_actual: str,
        password_nueva: str
    ) -> bool:
        """Cambiar contraseña"""
        success = await crud_usuario.change_password(
            db,
            usuario=usuario,
            password_actual=password_actual,
            password_nueva=password_nueva
        )
        
        if success:
            # Cerrar todas las sesiones excepto la actual
            await AuthService.logout_all_devices(db, str(usuario.id))
        
        return success
    
    @staticmethod
    async def generate_password_reset_token(db: AsyncSession, email: str) -> Optional[str]:
        """Generar token para reset de contraseña"""
        usuario = await crud_usuario.get_by_email(db, email)
        if not usuario:
            return None
        
        # Generar token único
        token = secrets.token_urlsafe(32)
        
        # Guardar en preferencias del usuario con expiración
        usuario.preferencias = usuario.preferencias or {}
        usuario.preferencias["reset_token"] = {
            "token": hashlib.sha256(token.encode()).hexdigest(),
            "expires": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        await db.flush()
        
        return token
    
    @staticmethod
    async def reset_password_with_token(
        db: AsyncSession,
        token: str,
        password_nueva: str
    ) -> bool:
        """Resetear contraseña con token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Buscar usuario con este token
        from sqlalchemy import select
        result = await db.execute(
            select(Usuario).where(Usuario.deleted_at.is_(None))
        )
        usuarios = result.scalars().all()
        
        for usuario in usuarios:
            if usuario.preferencias and usuario.preferencias.get("reset_token"):
                reset_data = usuario.preferencias["reset_token"]
                if (reset_data.get("token") == token_hash and
                    datetime.fromisoformat(reset_data.get("expires")) > datetime.utcnow()):
                    
                    await crud_usuario.reset_password(
                        db,
                        usuario=usuario,
                        password_nueva=password_nueva
                    )
                    
                    # Limpiar token
                    del usuario.preferencias["reset_token"]
                    await db.flush()
                    return True
        
        return False

# Instancia global
auth_service = AuthService()