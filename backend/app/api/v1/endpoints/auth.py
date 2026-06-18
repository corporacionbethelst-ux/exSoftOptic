from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UsuarioResponse
)
from app.api.deps import get_current_user
from app.models.usuario import Usuario

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login de usuario
    - Retorna access_token y refresh_token
    - Crea sesión en la base de datos
    """
    try:
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = await auth_service.login(
            db,
            login_data,
            ip=ip,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refrescar token de acceso
    - Requiere refresh_token válido
    - Retorna nuevos access_token y refresh_token
    """
    try:
        result = await auth_service.refresh_token(db, data.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar sesión actual
    - Invalida el token actual
    """
    success = await auth_service.logout(db, credentials.credentials)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo cerrar la sesión"
        )
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/logout-all-devices", status_code=status.HTTP_200_OK)
async def logout_all_devices(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar sesión en todos los dispositivos
    - Invalida todas las sesiones del usuario
    """
    count = await auth_service.logout_all_devices(db, str(current_user.id))
    return {
        "message": f"Sesiones cerradas: {count}",
        "sesiones_cerradas": count
    }

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cambiar contraseña
    - Requiere contraseña actual
    - Cierra todas las sesiones excepto la actual
    """
    if data.password_nueva != data.password_confirmacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden"
        )
    
    success = await auth_service.change_password(
        db,
        current_user,
        data.password_actual,
        data.password_nueva
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    return {"message": "Contraseña cambiada exitosamente"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Solicitar recuperación de contraseña
    - Envía email con token de recuperación
    - No revela si el email existe (seguridad)
    """
    token = await auth_service.generate_password_reset_token(db, data.email)
    
    # TODO: Enviar email con el token
    # Por ahora solo retornamos el token para testing
    if token:
        return {
            "message": "Si el email existe, recibirás instrucciones",
            "token": token  # Solo para desarrollo, remover en producción
        }
    
    return {"message": "Si el email existe, recibirás instrucciones"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Resetear contraseña con token
    - Valida token de recuperación
    - Actualiza contraseña
    """
    if data.password_nueva != data.password_confirmacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden"
        )
    
    success = await auth_service.reset_password_with_token(
        db,
        data.token,
        data.password_nueva
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    return {"message": "Contraseña reseteada exitosamente"}

@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    - Requiere token válido
    """
    return current_user

@router.get("/sessions", status_code=status.HTTP_200_OK)
async def get_active_sessions(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener sesiones activas del usuario
    """
    from sqlalchemy import select
    from app.models.usuario import Sesion
    
    result = await db.execute(
        select(Sesion).where(
            Sesion.usuario_id == current_user.id,
            Sesion.es_activa == True
        ).order_by(Sesion.ultima_actividad.desc())
    )
    sesiones = result.scalars().all()
    
    return {
        "total": len(sesiones),
        "sessions": [
            {
                "id": str(s.id),
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "dispositivo": s.dispositivo,
                "ultima_actividad": s.ultima_actividad.isoformat() if s.ultima_actividad else None,
                "expira_en": s.expira_en.isoformat() if s.expira_en else None
            }
            for s in sesiones
        ]
    }