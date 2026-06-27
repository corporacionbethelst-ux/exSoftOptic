from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import get_request_context
from app.models.usuario import Usuario
from app.schemas.auditoria import AuditoriaEventoCreate
from app.services.audit_service import AuditService


async def audit_user_action(
    db: AsyncSession,
    *,
    current_user: Usuario,
    accion: str,
    entidad: str,
    entidad_id: UUID | str | None = None,
    payload: dict | None = None,
    descripcion: str | None = None,
):
    context = get_request_context()
    return await AuditService(db).record_event(
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        payload=AuditoriaEventoCreate(
            accion=accion,
            entidad=entidad,
            entidad_id=str(entidad_id) if entidad_id is not None else None,
            payload={**(payload or {}), **({"correlation_id": context.correlation_id} if context else {})},
            descripcion=descripcion,
        ),
        ip_address=context.ip_address if context else None,
        user_agent=context.user_agent if context else None,
    )
