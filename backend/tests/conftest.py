import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.main import app
from httpx import AsyncClient

# Base de datos de prueba
TEST_DATABASE_URL = "postgresql+asyncpg://optica_user:optica_password_2026@localhost:5432/optica_test"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=True)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db_session():
    """Crear sesión de base de datos para tests"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_test() as session:
        yield session
    
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session):
    """Cliente HTTP para tests"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()