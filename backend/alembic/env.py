# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz del backend al path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base

# ============================================================================
# IMPORTAR MODELOS REGISTRADOS PARA AUTOGENERATE
# ============================================================================
# Importar módulos reales de modelos garantiza que Base.metadata contenga todas
# las tablas al ejecutar `alembic revision --autogenerate` y falla rápido si un
# modelo deja de existir o cambia de nombre.
from app.models import (
    auditoria,
    compra,
    configuracion,
    contabilidad,
    crm,
    empresa,
    factura,
    garantia,
    idempotencia,
    inventario,
    laboratorio,
    nomina,
    outbox,
    presupuesto,
    producto,
    sucursal,
    tesoreria,
    usuario,
    venta,
)

# ============================================================================
# CONFIGURACIÓN DE ALEMBIC
# ============================================================================

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sobrescribir URL con la configuración de la aplicación
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadata para 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Ejecutar migraciones con una conexión"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Ejecutar migraciones asíncronas"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo 'online'"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()