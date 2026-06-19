# backend/app/api/v1/router.py
from fastapi import APIRouter

# Importar SOLO los módulos que ya existen
from app.api.v1.endpoints import auth, compras, contabilidad, facturacion, garantias, inventario, laboratorio, productos, reportes, usuarios, ventas

api_router = APIRouter()

# Módulos implementados
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(productos.router, prefix="/productos", tags=["Productos"])
api_router.include_router(inventario.router, prefix="/inventario", tags=["Inventario"])
api_router.include_router(contabilidad.router, prefix="/contabilidad", tags=["Contabilidad"])
api_router.include_router(ventas.router, prefix="/ventas", tags=["Ventas"])
api_router.include_router(compras.router, prefix="/compras", tags=["Compras"])
api_router.include_router(laboratorio.router, prefix="/laboratorio", tags=["Laboratorio"])
api_router.include_router(garantias.router, prefix="/garantias", tags=["Garantías"])
api_router.include_router(facturacion.router, prefix="/facturacion", tags=["Facturación"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])

# Los siguientes se agregarán cuando se implementen en el Paso 4 y siguientes:
# api_router.include_router(productos.router, prefix="/productos", tags=["Productos"])
# api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
# api_router.include_router(proveedores.router, prefix="/proveedores", tags=["Proveedores"])
# api_router.include_router(ventas.router, prefix="/ventas", tags=["Ventas"])
# api_router.include_router(compras.router, prefix="/compras", tags=["Compras"])
# api_router.include_router(inventario.router, prefix="/inventario", tags=["Inventario"])
# api_router.include_router(contabilidad.router, prefix="/contabilidad", tags=["Contabilidad"])
# api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
