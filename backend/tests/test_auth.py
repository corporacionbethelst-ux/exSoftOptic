from datetime import datetime, timedelta, timezone
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.empresa import Empresa
from app.models.usuario import Rol, Sesion, Usuario


AUTH_USERNAME = "testuser"
AUTH_PASSWORD = "Test123!"


@pytest.fixture
async def auth_user(db_session: AsyncSession) -> Usuario:
    """Create an isolated active user for auth endpoint tests."""
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Test SA",
        rfc=f"TST{uuid.uuid4().hex[:9].upper()}",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    db_session.add(empresa)
    await db_session.flush()

    rol = Rol(
        id=uuid.uuid4(),
        nombre=f"TEST_USER_{uuid.uuid4().hex[:8].upper()}",
        permisos=["*"],
        empresa_id=empresa.id,
    )
    db_session.add(rol)
    await db_session.flush()

    user = Usuario(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        username=AUTH_USERNAME,
        email="test@test.com",
        password_hash=get_password_hash(AUTH_PASSWORD),
        nombre_completo="Test User",
        rol_id=rol.id,
        esta_activo=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


async def login(
    client: AsyncClient,
    username: str = AUTH_USERNAME,
    password: str = AUTH_PASSWORD,
):
    return await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_user: Usuario,
):
    """Test de login exitoso."""
    response = await login(client)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    session = (
        await db_session.execute(
            select(Sesion).where(Sesion.usuario_id == auth_user.id)
        )
    ).scalar_one()
    minimum_refresh_expiry = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS - 1
    )
    assert session.expira_en > minimum_refresh_expiry


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test de login con credenciales inválidas."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "invalid", "password": "wrong"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_user: Usuario):
    """Test obtener usuario actual."""
    login_response = await login(client)
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == auth_user.username


@pytest.mark.asyncio
async def test_refresh_token_rotates_session(client: AsyncClient, auth_user: Usuario):
    """Test refresh token and invalidate the previous refresh token."""
    login_response = await login(client)
    original_refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != original_refresh_token

    reused_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    assert reused_response.status_code == 401

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == auth_user.username


@pytest.mark.asyncio
async def test_logout_invalidates_access_token(client: AsyncClient, auth_user: Usuario):
    """Test logout."""
    login_response = await login(client)
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 401


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, auth_user: Usuario):
    """Test cambio de contraseña."""
    login_response = await login(client)
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password_actual": AUTH_PASSWORD,
            "password_nueva": "NewAdmin123!",
            "password_confirmacion": "NewAdmin123!",
        },
    )

    assert response.status_code == 200

    login_response2 = await login(client, password="NewAdmin123!")
    assert login_response2.status_code == 200
    assert login_response2.json()["user"]["username"] == auth_user.username
