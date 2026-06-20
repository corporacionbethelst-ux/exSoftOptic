from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import async_session_maker, get_db
from app.core.metrics import runtime_metrics
from app.models.usuario import Usuario
from app.services.idempotency_service import IdempotencyService

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


@router.post("/maintenance/idempotency/cleanup", dependencies=[Depends(require_permissions(["observabilidad.mantenimiento.ejecutar"]))])
async def limpiar_idempotency_keys_expiradas(
    limit: int = Query(500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """Elimina claves idempotentes expiradas del tenant actual para controlar crecimiento operacional."""
    deleted = await IdempotencyService(db).cleanup_expired(empresa_id=current_user.empresa_id, limit=limit)
    return {"deleted": deleted, "limit": limit}
