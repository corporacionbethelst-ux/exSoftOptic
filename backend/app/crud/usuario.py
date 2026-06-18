from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.usuario import Usuario, Rol, Sesion
from app.schemas.auth import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """CRUD específico para usuarios"""
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[Usuario]:
        """Obtener usuario por username"""
        result = await db.execute(
            select(Usuario).where(
                and_(
                    Usuario.username == username,
                    Usuario.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Usuario]:
        """Obtener usuario por email"""
        result = await db.execute(
            select(Usuario).where(
                and_(
                    Usuario.email == email,
                    Usuario.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        username: str,
        password: str
    ) -> Optional[Usuario]:
        """Autenticar usuario"""
        usuario = await self.get_by_username(db, username)
        
        if not usuario:
            return None
        
        # Verificar si está bloqueado
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
            return None
        
        # Verificar si está activo
        if not usuario.esta_activo:
            return None
        
        # Verificar contraseña
        if not verify_password(password, usuario.password_hash):
            # Incrementar intentos fallidos
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= 5:
                usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=15)
            await db.flush()
            return None
        
        # Resetear intentos fallidos
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.ultimo_acceso = datetime.utcnow()
        await db.flush()
        
        return usuario
    
    async def create_with_password(
        self,
        db: AsyncSession,
        *,
        obj_in: UsuarioCreate
    ) -> Usuario:
        """Crear usuario con contraseña hasheada"""
        # Verificar username único
        if await self.get_by_username(db, obj_in.username):
            raise ValueError("El username ya está en uso")
        
        # Verificar email único
        if await self.get_by_email(db, obj_in.email):
            raise ValueError("El email ya está en uso")
        
        # Crear usuario
        usuario_data = obj_in.model_dump()
        usuario_data["password_hash"] = get_password_hash(obj_in.password)
        usuario_data["id"] = UUID(obj_in.get("id") if hasattr(obj_in, "get") else None) if hasattr(obj_in, "get") else None
        
        # Remover password del dict
        usuario_data.pop("password", None)
        
        db_obj = Usuario(**usuario_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def change_password(
        self,
        db: AsyncSession,
        *,
        usuario: Usuario,
        password_actual: str,
        password_nueva: str
    ) -> bool:
        """Cambiar contraseña"""
        if not verify_password(password_actual, usuario.password_hash):
            return False
        
        usuario.password_hash = get_password_hash(password_nueva)
        await db.flush()
        return True
    
    async def reset_password(
        self,
        db: AsyncSession,
        *,
        usuario: Usuario,
        password_nueva: str
    ) -> bool:
        """Resetear contraseña (sin verificar la actual)"""
        usuario.password_hash = get_password_hash(password_nueva)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        await db.flush()
        return True
    
    async def get_with_rol(self, db: AsyncSession, id: str) -> Optional[Usuario]:
        """Obtener usuario con rol cargado"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .where(
                and_(
                    Usuario.id == UUID(id),
                    Usuario.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_multi_with_rol(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[Usuario]:
        """Obtener usuarios con roles cargados"""
        from sqlalchemy.orm import selectinload
        query = (
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .where(Usuario.deleted_at.is_(None))
        )
        
        if filters:
            for field, value in filters.items():
                if hasattr(Usuario, field) and value is not None:
                    query = query.where(getattr(Usuario, field) == value)
        
        query = query.offset(skip).limit(limit).order_by(Usuario.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()

class CRUDRol(CRUDBase[Rol, any, any]):
    """CRUD para roles"""
    
    async def get_by_nombre(self, db: AsyncSession, nombre: str) -> Optional[Rol]:
        result = await db.execute(
            select(Rol).where(Rol.nombre == nombre)
        )
        return result.scalar_one_or_none()

# Instancias globales
crud_usuario = CRUDUsuario(Usuario)
crud_rol = CRUDRol(Rol)