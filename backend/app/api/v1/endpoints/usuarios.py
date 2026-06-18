from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.crud.usuario import crud_usuario, crud_rol
from app.schemas.auth import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse,
    UsuarioPerfilUpdate,
    RolCreate,
    RolResponse
)
from app.api.deps import (
    get_current_user,
    require_permissions,
    require_role
)
from app.models.usuario import Usuario

router = APIRouter()

# ============================================================================
# GESTIÓN DE USUARIOS (Admin)
# ============================================================================

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UsuarioCreate,
    current_user: Usuario = Depends(require_permissions(["usuarios.crear"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear nuevo usuario
    - Requiere permiso: usuarios.crear
    """
    try:
        # Verificar que el usuario actual pueda crear usuarios del rol especificado
        if current_user.rol.nivel_acceso <= 5 and user_in.rol_id != str(current_user.rol_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear usuarios con diferentes roles"
            )
        
        usuario = await crud_usuario.create_with_password(db, obj_in=user_in)
        usuario_completo = await crud_usuario.get_with_rol(db, str(usuario.id))
        return usuario_completo
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=UsuarioListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    rol_id: Optional[str] = None,
    sucursal_id: Optional[str] = None,
    esta_activo: Optional[bool] = None,
    current_user: Usuario = Depends(require_permissions(["usuarios.ver"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar usuarios con paginación y filtros
    - Requiere permiso: usuarios.ver
    """
    skip = (page - 1) * per_page
    
    filters = {}
    if rol_id:
        filters["rol_id"] = UUID(rol_id)
    if sucursal_id:
        filters["sucursal_id"] = UUID(sucursal_id)
    if esta_activo is not None:
        filters["esta_activo"] = esta_activo
    
    # Si no es admin global, solo ver usuarios de su sucursal
    if current_user.sucursal_id:
        filters["sucursal_id"] = current_user.sucursal_id
    
    usuarios = await crud_usuario.get_multi_with_rol(
        db,
        skip=skip,
        limit=per_page,
        filters=filters
    )
    
    total = await crud_usuario.count(db, filters=filters)
    
    return UsuarioListResponse(
        total=total,
        page=page,
        per_page=per_page,
        users=usuarios
    )

@router.get("/{user_id}", response_model=UsuarioResponse)
async def get_user(
    user_id: str,
    current_user: Usuario = Depends(require_permissions(["usuarios.ver"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener usuario por ID
    - Requiere permiso: usuarios.ver
    """
    usuario = await crud_usuario.get_with_rol(db, user_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar permisos de sucursal
    if current_user.sucursal_id and usuario.sucursal_id != current_user.sucursal_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este usuario"
        )
    
    return usuario

@router.put("/{user_id}", response_model=UsuarioResponse)
async def update_user(
    user_id: str,
    user_in: UsuarioUpdate,
    current_user: Usuario = Depends(require_permissions(["usuarios.editar"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar usuario
    - Requiere permiso: usuarios.editar
    """
    usuario = await crud_usuario.get(db, user_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar permisos de sucursal
    if current_user.sucursal_id and usuario.sucursal_id != current_user.sucursal_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes editar usuarios de otras sucursales"
        )
    
    # Verificar que no se desactive a sí mismo
    if user_in.esta_activo == False and str(usuario.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    # Verificar email único si se cambia
    if user_in.email and user_in.email != usuario.email:
        if await crud_usuario.get_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    
    usuario_actualizado = await crud_usuario.update(db, db_obj=usuario, obj_in=user_in)
    usuario_completo = await crud_usuario.get_with_rol(db, str(usuario_actualizado.id))
    return usuario_completo

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    current_user: Usuario = Depends(require_permissions(["usuarios.eliminar"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar usuario (soft delete)
    - Requiere permiso: usuarios.eliminar
    """
    usuario = await crud_usuario.get(db, user_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No puede eliminarse a sí mismo
    if str(usuario.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    
    # No puede eliminar super admin
    if usuario.rol and usuario.rol.nombre == "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar un super administrador"
        )
    
    await crud_usuario.delete(db, id=user_id)
    return {"message": "Usuario eliminado exitosamente"}

# ============================================================================
# PERFIL DE USUARIO (Usuario actual)
# ============================================================================

@router.get("/me/profile", response_model=UsuarioResponse)
async def get_my_profile(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener mi perfil
    """
    return current_user

@router.put("/me/profile", response_model=UsuarioResponse)
async def update_my_profile(
    profile_in: UsuarioPerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar mi perfil
    """
    usuario_actualizado = await crud_usuario.update(
        db,
        db_obj=current_user,
        obj_in=profile_in
    )
    usuario_completo = await crud_usuario.get_with_rol(db, str(usuario_actualizado.id))
    return usuario_completo

# ============================================================================
# GESTIÓN DE ROLES
# ============================================================================

@router.get("/roles", response_model=List[RolResponse])
async def list_roles(
    current_user: Usuario = Depends(require_permissions(["usuarios.ver"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los roles
    """
    roles = await crud_rol.get_multi(db)
    return roles

@router.post("/roles", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RolCreate,
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear nuevo rol
    - Solo super administradores
    """
    # Verificar que el nombre sea único
    existing = await crud_rol.get_by_nombre(db, role_in.nombre)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del rol ya existe"
        )
    
    rol = await crud_rol.create(db, obj_in=role_in)
    return rol

@router.get("/roles/{role_id}", response_model=RolResponse)
async def get_role(
    role_id: str,
    current_user: Usuario = Depends(require_permissions(["usuarios.ver"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener rol por ID
    """
    rol = await crud_rol.get(db, role_id)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    return rol