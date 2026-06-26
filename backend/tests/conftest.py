import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Defaults seguros para importar la app en pruebas sin depender de un .env local.
os.environ.setdefault("SECRET_KEY", "test_secret_key_change_me")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://optica_user:optica_password_2026@localhost:5432/optica_system")
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017/optica_clinico")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
import app.models  # noqa: F401,E402  # registra todos los modelos en Base.metadata

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://optica_user:optica_password_2026@localhost:5432/optica_test",
)

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def db_session():
    """Crear una base limpia por test usando los modelos registrados."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_test() as session:
        yield session
        await session.rollback()

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Cliente HTTP conectado a la sesión transaccional de prueba."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()
