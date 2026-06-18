from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

# ============================================================================
# SCHEMAS DE AUTENTICACIÓN
# ============================================================================

class LoginRequest(BaseModel):
    """Schema para login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class LoginResponse(BaseModel):
    """Respuesta del login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UsuarioResponse"

class TokenData(BaseModel):
    """Datos del token decodificado"""
    user_id: str
    username: str
    email: str
    rol: str
    sucursal_id: Optional[str] = None
    empresa_id: str

class RefreshTokenRequest(BaseModel):
    """Solicitud de refresh token"""
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    """Cambio de contraseña"""
    password_actual: str = Field(..., min_length=6)
    password_nueva: str = Field(..., min_length=8, max_length=100)
    password_confirmacion: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password_nueva')
    def validar_password_fuerte(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Debe contener al menos un carácter especial')
        return v

class ForgotPasswordRequest(BaseModel):
    """Solicitud de recuperación de contraseña"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Reset de contraseña con token"""
    token: str
    password_nueva: str = Field(..., min_length=8, max_length=100)
    password_confirmacion: str = Field(..., min_length=8, max_length=100)

# ============================================================================
# SCHEMAS DE USUARIO
# ============================================================================

class UsuarioBase(BaseModel):
    """Schema base de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nombre_completo: str = Field(..., min_length=3, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20)

class UsuarioCreate(UsuarioBase):
    """Crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)
    rol_id: str
    sucursal_id: Optional[str] = None
    
    @field_validator('password')
    def validar_password_fuerte(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Debe contener al menos un número')
        return v

class UsuarioUpdate(BaseModel):
    """Actualizar usuario"""
    nombre_completo: Optional[str] = Field(None, min_length=3, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    rol_id: Optional[str] = None
    sucursal_id: Optional[str] = None
    esta_activo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    """Respuesta de usuario"""
    id: str
    rol_id: str
    sucursal_id: Optional[str] = None
    empresa_id: str
    esta_activo: bool
    email_verificado: bool
    ultimo_acceso: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UsuarioListResponse(BaseModel):
    """Lista de usuarios con paginación"""
    total: int
    page: int
    per_page: int
    users: list[UsuarioResponse]

class UsuarioPerfilUpdate(BaseModel):
    """Actualización de perfil por el propio usuario"""
    nombre_completo: Optional[str] = Field(None, min_length=3, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = None

# ============================================================================
# SCHEMAS DE ROL
# ============================================================================

class RolBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
    descripcion: Optional[str] = None
    nivel_acceso: int = Field(default=1, ge=1, le=10)

class RolCreate(RolBase):
    permisos: list[str] = []

class RolResponse(RolBase):
    id: str
    es_sistema: bool
    permisos: list[str] = []
    esta_activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Actualizar forward references
LoginResponse.model_rebuild()