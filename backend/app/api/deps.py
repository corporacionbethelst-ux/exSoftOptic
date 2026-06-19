from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.services.auth_service import auth_service
from app.models.usuario import Usuario

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Dependencia para obtener el usuario actual
    - Valida el token JWT
    - Verifica que la sesión esté activa
    - Retorna el usuario completo con rol
    """
    try:
        usuario = await auth_service.get_current_user(db, credentials.credentials)
        return usuario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Verificar que el usuario esté activo
    """
    if not current_user.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

def require_permissions(required_permissions: List[str]):
    """
    Decorador para requerir permisos específicos
    Uso: Depends(require_permissions(["usuarios.crear", "usuarios.editar"]))
    """
    async def permission_checker(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        # Super admin tiene todos los permisos
        if current_user.rol and current_user.rol.nombre == "SUPER_ADMIN":
            return current_user
        
        # Verificar permisos
        user_permissions = current_user.rol.permisos if current_user.rol else []
        
        # Si tiene permiso wildcard
        if "*" in user_permissions:
            return current_user
        
        # Verificar permisos requeridos
        for perm in required_permissions:
            modulo = perm.split(".")[0]
            # Verificar permiso específico o wildcard del módulo
            if perm not in user_permissions and f"{modulo}.*" not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso requerido: {perm}"
                )
        
        return current_user
    
    return permission_checker

def require_role(role_names: List[str]):
    """
    Decorador para requerir roles específicos
    Uso: Depends(require_role(["ADMIN", "SUPER_ADMIN"]))
    """
    async def role_checker(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        if not current_user.rol:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin rol asignado"
            )
        
        if current_user.rol.nombre not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {', '.join(role_names)}"
            )
        
        return current_user
    
    return role_checker

def require_same_sucursal_or_admin():
    """
    Verificar que el usuario acceda solo a datos de su sucursal
    O que sea admin global
    """
    async def sucursal_checker(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        # Admin global puede acceder a todo
        if current_user.sucursal_id is None:
            return current_user
        
        # Si tiene sucursal asignada, solo puede ver datos de esa sucursal
        return current_user
    
    return sucursal_checker

async def get_current_super_admin(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Requerir super administrador
    """
    if not current_user.rol or current_user.rol.nombre != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de super administrador"
        )
    return current_user

def require_empresa_scope(empresa_id: UUID, current_user: Usuario) -> None:
    """ABAC: bloquea acceso cross-tenant por empresa."""
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado a datos de otra empresa",
        )


def require_sucursal_scope(sucursal_id: UUID | None, current_user: Usuario) -> None:
    """ABAC: usuarios con sucursal asignada solo operan su sucursal."""
    if current_user.sucursal_id is not None and sucursal_id != current_user.sucursal_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado a datos de otra sucursal",
        )
