import asyncio
import uuid
from sqlalchemy import select

from app.core.database import async_session_maker, engine, Base
from app.core.security import get_password_hash
from app.models.usuario import Usuario, Rol
from app.models.empresa import Empresa
from app.models.sucursal import Sucursal

async def _upsert_by_scalar(db, model, lookup, values, label):
    """Crear o actualizar una fila usando un criterio único."""
    record = await db.scalar(select(model).where(*lookup))
    action = "actualizado"

    if record is None:
        record = model(id=uuid.uuid4(), **values)
        db.add(record)
        action = "creado"
    else:
        for field, value in values.items():
            setattr(record, field, value)

    await db.flush()
    print(f"  ✅ {label} {action}: {getattr(record, 'id', '')}")
    return record


async def create_initial_data():
    """Crear o actualizar datos iniciales del sistema de forma idempotente."""

    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # 1. Crear o actualizar empresa principal
        print("🏢 Preparando empresa principal...")
        empresa = await _upsert_by_scalar(
            db,
            Empresa,
            (Empresa.rfc == "ODE260618ABC",),
            {
                "razon_social": "Óptica Demo S.A. de C.V.",
                "nombre_comercial": "Óptica Demo",
                "rfc": "ODE260618ABC",
                "regimen_fiscal": "601",
                "codigo_postal": "06600",
                "representante_legal": "Admin Demo",
                "moneda_base": "MXN",
            },
            "Empresa",
        )

        # 2. Crear o actualizar sucursal principal
        print("🏪 Preparando sucursal principal...")
        sucursal = await _upsert_by_scalar(
            db,
            Sucursal,
            (Sucursal.empresa_id == empresa.id, Sucursal.codigo == "MAIN"),
            {
                "empresa_id": empresa.id,
                "codigo": "MAIN",
                "nombre": "Sucursal Principal",
                "direccion": "Av. Reforma 123",
                "ciudad": "Ciudad de México",
                "estado": "CDMX",
                "codigo_postal": "06600",
                "es_principal": True,
            },
            "Sucursal",
        )

        # 3. Crear o actualizar roles del sistema
        print("👥 Preparando roles...")
        roles_data = [
            {
                "nombre": "SUPER_ADMIN",
                "descripcion": "Acceso total al sistema",
                "es_sistema": True,
                "nivel_acceso": 10,
                "permisos": ["*"],
                "empresa_id": empresa.id,
            },
            {
                "nombre": "ADMIN_SUCURSAL",
                "descripcion": "Administrador de sucursal",
                "es_sistema": True,
                "nivel_acceso": 8,
                "permisos": ["*"],
                "empresa_id": empresa.id,
            },
            {
                "nombre": "OPTOMETRISTA",
                "descripcion": "Optometrista con acceso clínico",
                "es_sistema": True,
                "nivel_acceso": 6,
                "permisos": [
                    "clientes.*", "citas.*", "expedientes.*",
                    "recetas.*", "ventas.ver", "agenda.*",
                ],
                "empresa_id": empresa.id,
            },
            {
                "nombre": "VENDEDOR",
                "descripcion": "Vendedor de mostrador",
                "es_sistema": True,
                "nivel_acceso": 5,
                "permisos": [
                    "clientes.ver", "clientes.crear", "ventas.*",
                    "caja.*", "productos.ver",
                ],
                "empresa_id": empresa.id,
            },
            {
                "nombre": "ALMACENISTA",
                "descripcion": "Responsable de inventario",
                "es_sistema": True,
                "nivel_acceso": 4,
                "permisos": [
                    "inventario.*", "productos.ver", "ordenes_compra.*",
                ],
                "empresa_id": empresa.id,
            },
            {
                "nombre": "CONTADOR",
                "descripcion": "Acceso a contabilidad",
                "es_sistema": True,
                "nivel_acceso": 7,
                "permisos": [
                    "contabilidad.*", "reportes.*", "facturas.*",
                    "cuentas_cobrar.*", "cuentas_pagar.*",
                ],
                "empresa_id": empresa.id,
            },
        ]

        roles = {}
        for rol_data in roles_data:
            rol = await _upsert_by_scalar(
                db,
                Rol,
                (Rol.nombre == rol_data["nombre"],),
                rol_data,
                f"Rol {rol_data['nombre']}",
            )
            roles[rol_data["nombre"]] = rol

        # 4. Crear o actualizar usuario administrador
        print("👤 Preparando usuario administrador...")
        await _upsert_by_scalar(
            db,
            Usuario,
            (Usuario.username == "admin",),
            {
                "empresa_id": empresa.id,
                "username": "admin",
                "email": "admin@optica.com",
                "password_hash": get_password_hash("Admin123!"),
                "nombre_completo": "Administrador del Sistema",
                "rol_id": roles["SUPER_ADMIN"].id,
                "sucursal_id": None,  # Admin global
                "esta_activo": True,
                "email_verificado": True,
            },
            "Usuario admin",
        )

        # 5. Crear o actualizar usuarios de ejemplo
        print("👥 Preparando usuarios de ejemplo...")
        usuarios_demo = [
            {
                "username": "admin_sucursal",
                "email": "admin_sucursal@optica.com",
                "nombre": "Admin Sucursal Demo",
                "rol": "ADMIN_SUCURSAL",
                "sucursal": sucursal.id,
            },
            {
                "username": "optometrista",
                "email": "optometrista@optica.com",
                "nombre": "Dr. Demo Optometrista",
                "rol": "OPTOMETRISTA",
                "sucursal": sucursal.id,
            },
            {
                "username": "vendedor",
                "email": "vendedor@optica.com",
                "nombre": "Vendedor Demo",
                "rol": "VENDEDOR",
                "sucursal": sucursal.id,
            },
            {
                "username": "contador",
                "email": "contador@optica.com",
                "nombre": "Contador Demo",
                "rol": "CONTADOR",
                "sucursal": sucursal.id,
            },
        ]

        for user_data in usuarios_demo:
            await _upsert_by_scalar(
                db,
                Usuario,
                (Usuario.username == user_data["username"],),
                {
                    "empresa_id": empresa.id,
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password_hash": get_password_hash("Demo123!"),
                    "nombre_completo": user_data["nombre"],
                    "rol_id": roles[user_data["rol"]].id,
                    "sucursal_id": user_data["sucursal"],
                    "esta_activo": True,
                    "email_verificado": True,
                },
                f"Usuario {user_data['username']}",
            )

        await db.commit()

        print("\n" + "="*60)
        print("🎉 DATOS INICIALES PREPARADOS EXITOSAMENTE")
        print("="*60)
        print("\n📋 CREDENCIALES DE ACCESO:")
        print("-"*60)
        print("👑 Admin Principal:")
        print("   Username: admin")
        print("   Password: Admin123!")
        print("\n👥 Usuarios Demo (Password: Demo123!):")
        print("   - admin_sucursal (Admin de Sucursal)")
        print("   - optometrista (Optometrista)")
        print("   - vendedor (Vendedor)")
        print("   - contador (Contador)")
        print("="*60)

if __name__ == "__main__":
    print("🚀 Iniciando creación de datos iniciales...\n")
    asyncio.run(create_initial_data())