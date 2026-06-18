import asyncio
import uuid
from datetime import datetime
from sqlalchemy import select

from app.core.database import async_session_maker, engine, Base
from app.core.security import get_password_hash
from app.models.usuario import Usuario, Rol
from app.models.empresa import Empresa
from app.models.sucursal import Sucursal

async def create_initial_data():
    """Crear datos iniciales del sistema"""
    
    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as db:
        # 1. Crear empresa principal
        print("🏢 Creando empresa principal...")
        empresa = Empresa(
            id=uuid.uuid4(),
            razon_social="Óptica Demo S.A. de C.V.",
            nombre_comercial="Óptica Demo",
            rfc="ODE260618ABC",
            regimen_fiscal="601",
            codigo_postal="06600",
            representante_legal="Admin Demo",
            moneda_base="MXN"
        )
        db.add(empresa)
        await db.flush()
        print(f"✅ Empresa creada: {empresa.id}")
        
        # 2. Crear sucursal principal
        print("🏪 Creando sucursal principal...")
        sucursal = Sucursal(
            id=uuid.uuid4(),
            empresa_id=empresa.id,
            codigo="MAIN",
            nombre="Sucursal Principal",
            direccion="Av. Reforma 123",
            ciudad="Ciudad de México",
            estado="CDMX",
            codigo_postal="06600",
            es_principal=True
        )
        db.add(sucursal)
        await db.flush()
        print(f"✅ Sucursal creada: {sucursal.id}")
        
        # 3. Crear roles del sistema
        print("👥 Creando roles...")
        roles_data = [
            {
                "nombre": "SUPER_ADMIN",
                "descripcion": "Acceso total al sistema",
                "es_sistema": True,
                "nivel_acceso": 10,
                "permisos": ["*"],
                "empresa_id": empresa.id
            },
            {
                "nombre": "ADMIN_SUCURSAL",
                "descripcion": "Administrador de sucursal",
                "es_sistema": True,
                "nivel_acceso": 8,
                "permisos": ["*"],
                "empresa_id": empresa.id
            },
            {
                "nombre": "OPTOMETRISTA",
                "descripcion": "Optometrista con acceso clínico",
                "es_sistema": True,
                "nivel_acceso": 6,
                "permisos": [
                    "clientes.*", "citas.*", "expedientes.*",
                    "recetas.*", "ventas.ver", "agenda.*"
                ],
                "empresa_id": empresa.id
            },
            {
                "nombre": "VENDEDOR",
                "descripcion": "Vendedor de mostrador",
                "es_sistema": True,
                "nivel_acceso": 5,
                "permisos": [
                    "clientes.ver", "clientes.crear", "ventas.*",
                    "caja.*", "productos.ver"
                ],
                "empresa_id": empresa.id
            },
            {
                "nombre": "ALMACENISTA",
                "descripcion": "Responsable de inventario",
                "es_sistema": True,
                "nivel_acceso": 4,
                "permisos": [
                    "inventario.*", "productos.ver", "ordenes_compra.*"
                ],
                "empresa_id": empresa.id
            },
            {
                "nombre": "CONTADOR",
                "descripcion": "Acceso a contabilidad",
                "es_sistema": True,
                "nivel_acceso": 7,
                "permisos": [
                    "contabilidad.*", "reportes.*", "facturas.*",
                    "cuentas_cobrar.*", "cuentas_pagar.*"
                ],
                "empresa_id": empresa.id
            }
        ]
        
        roles = {}
        for rol_data in roles_data:
            rol = Rol(**rol_data)
            db.add(rol)
            roles[rol_data["nombre"]] = rol
            print(f"  ✅ Rol creado: {rol_data['nombre']}")
        
        await db.flush()
        
        # 4. Crear usuario administrador
        print("👤 Creando usuario administrador...")
        admin = Usuario(
            id=uuid.uuid4(),
            empresa_id=empresa.id,
            username="admin",
            email="admin@optica.com",
            password_hash=get_password_hash("Admin123!"),
            nombre_completo="Administrador del Sistema",
            rol_id=roles["SUPER_ADMIN"].id,
            sucursal_id=None,  # Admin global
            esta_activo=True,
            email_verificado=True
        )
        db.add(admin)
        print(f"✅ Admin creado: {admin.username}")
        
        # 5. Crear usuarios de ejemplo
        print("👥 Creando usuarios de ejemplo...")
        usuarios_demo = [
            {
                "username": "admin_sucursal",
                "email": "admin_sucursal@optica.com",
                "nombre": "Admin Sucursal Demo",
                "rol": "ADMIN_SUCURSAL",
                "sucursal": sucursal.id
            },
            {
                "username": "optometrista",
                "email": "optometrista@optica.com",
                "nombre": "Dr. Demo Optometrista",
                "rol": "OPTOMETRISTA",
                "sucursal": sucursal.id
            },
            {
                "username": "vendedor",
                "email": "vendedor@optica.com",
                "nombre": "Vendedor Demo",
                "rol": "VENDEDOR",
                "sucursal": sucursal.id
            },
            {
                "username": "contador",
                "email": "contador@optica.com",
                "nombre": "Contador Demo",
                "rol": "CONTADOR",
                "sucursal": sucursal.id
            }
        ]
        
        for user_data in usuarios_demo:
            user = Usuario(
                id=uuid.uuid4(),
                empresa_id=empresa.id,
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash("Demo123!"),
                nombre_completo=user_data["nombre"],
                rol_id=roles[user_data["rol"]].id,
                sucursal_id=user_data["sucursal"],
                esta_activo=True,
                email_verificado=True
            )
            db.add(user)
            print(f"  ✅ Usuario creado: {user_data['username']}")
        
        await db.commit()
        
        print("\n" + "="*60)
        print("🎉 DATOS INICIALES CREADOS EXITOSAMENTE")
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