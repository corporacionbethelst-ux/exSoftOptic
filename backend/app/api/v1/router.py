from fastapi import APIRouter

from app.api.v1.endpoints import auth, auditoria, compras, configuracion, contabilidad, crm, facturacion, garantias, inventario, laboratorio, nomina, observabilidad, outbox, presupuestos, productos, reportes, tesoreria, usuarios, ventas

api_router = APIRouter()

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
api_router.include_router(nomina.router, prefix="/nomina", tags=["Nómina"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoría"])
api_router.include_router(configuracion.router, prefix="/configuracion", tags=["Configuración"])
api_router.include_router(crm.router, prefix="/crm", tags=["CRM"])
api_router.include_router(tesoreria.router, prefix="/tesoreria", tags=["Tesorería"])
api_router.include_router(presupuestos.router, prefix="/presupuestos", tags=["Presupuestos"])
api_router.include_router(observabilidad.router, prefix="/observabilidad", tags=["Observabilidad"])
api_router.include_router(outbox.router, prefix="/outbox", tags=["Outbox Transaccional"])
