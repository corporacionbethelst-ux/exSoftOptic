from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.deps import require_permissions
from app.core.database import async_session_maker
from app.core.metrics import runtime_metrics

router = APIRouter()


@router.get("/metrics", dependencies=[Depends(require_permissions(["observabilidad.metricas.leer"]))])
async def obtener_metricas_runtime():
    """Retorna métricas runtime protegidas por permisos para operación/SRE."""
    return runtime_metrics.snapshot()


@router.get("/readiness")
async def verificar_readiness():
    """Verifica que la API pueda abrir sesión y ejecutar una consulta mínima."""
    async with async_session_maker() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ready", "database": "reachable"}
