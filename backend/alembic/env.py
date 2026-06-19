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
# IMPORTAR SOLO LOS MODELOS QUE EXISTEN ACTUALMENTE
# ============================================================================
# A medida que crees más modelos, agrégalos aquí

try:
    from app.models import empresa
except ImportError:
    pass

try:
    from app.models import sucursal
except ImportError:
    pass

try:
    from app.models import usuario
except ImportError:
    pass

try:
    from app.models import producto
except ImportError:
    pass

try:
    from app.models import cliente
except ImportError:
    pass

try:
    from app.models import proveedor
except ImportError:
    pass

try:
    from app.models import inventario
except ImportError:
    pass

try:
    from app.models import venta
except ImportError:
    pass

try:
    from app.models import compra
except ImportError:
    pass

try:
    from app.models import laboratorio
except ImportError:
    pass

try:
    from app.models import garantia
except ImportError:
    pass

try:
    from app.models import factura
except ImportError:
    pass

try:
    from app.models import contabilidad
except ImportError:
    pass

try:
    from app.models import tesoreria
except ImportError:
    pass

try:
    from app.models import nomina
except ImportError:
    pass

try:
    from app.models import auditoria
except ImportError:
    pass

try:
    from app.models import configuracion
except ImportError:
    pass

try:
    from app.models import crm
except ImportError:
    pass

try:
    from app.models import presupuesto
except ImportError:
    pass

from app.models import outbox

try:
    from app.models import activo_fijo
except ImportError:
    pass

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