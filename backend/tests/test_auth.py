import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.usuario import Usuario, Rol
from app.models.empresa import Empresa
import uuid

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """Test de login exitoso"""
    # Crear datos de prueba
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Test SA",
        rfc="TEST260618",
        regimen_fiscal="601",
        codigo_postal="06600"
    )
    db_session.add(empresa)
    await db_session.flush()
    
    rol = Rol(
        id=uuid.uuid4(),
        nombre="TEST_USER",
        permisos=["*"],
        empresa_id=empresa.id
    )
    db_session.add(rol)
    await db_session.flush()
    
    user = Usuario(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        username="testuser",
        email="test@test.com",
        password_hash=get_password_hash("Test123!"),
        nombre_completo="Test User",
        rol_id=rol.id,
        esta_activo=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test login
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test123!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test de login con credenciales inválidas"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "invalid", "password": "wrong"}
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db_session: AsyncSession):
    """Test obtener usuario actual"""
    # Login primero
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin123!"}
    )
    
    if login_response.status_code != 200:
        pytest.skip("Admin user not available")
    
    token = login_response.json()["access_token"]
    
    # Obtener usuario actual
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test refresh token"""
    # Login primero
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin123!"}
    )
    
    if login_response.status_code != 200:
        pytest.skip("Admin user not available")
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Refrescar token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout"""
    # Login primero
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin123!"}
    )
    
    if login_response.status_code != 200:
        pytest.skip("Admin user not available")
    
    token = login_response.json()["access_token"]
    
    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_change_password(client: AsyncClient):
    """Test cambio de contraseña"""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin123!"}
    )
    
    if login_response.status_code != 200:
        pytest.skip("Admin user not available")
    
    token = login_response.json()["access_token"]
    
    # Cambiar contraseña
    response = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password_actual": "Admin123!",
            "password_nueva": "NewAdmin123!",
            "password_confirmacion": "NewAdmin123!"
        }
    )
    
    assert response.status_code == 200
    
    # Volver a la contraseña original
    login_response2 = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "NewAdmin123!"}
    )
    token2 = login_response2.json()["access_token"]
    
    await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "password_actual": "NewAdmin123!",
            "password_nueva": "Admin123!",
            "password_confirmacion": "Admin123!"
        }
    )