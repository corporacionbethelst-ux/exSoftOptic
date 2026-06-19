from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.outbox import OutboxEventCreate, OutboxEventFailRequest, OutboxEventResponse
from app.services.outbox_service import OutboxService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/events", response_model=OutboxEventResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["outbox.eventos.crear"]))])
async def crear_evento_outbox(payload: OutboxEventCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    event = await OutboxService(db).enqueue(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="OUTBOX_EVENT_ENQUEUE", entidad="OutboxEvent", entidad_id=event.id, payload={"event_type": event.event_type, "aggregate_id": event.aggregate_id})
    return event


@router.get("/events/pending", response_model=list[OutboxEventResponse], dependencies=[Depends(require_permissions(["outbox.eventos.leer"]))])
async def listar_eventos_pendientes(limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await OutboxService(db).list_pending(empresa_id=current_user.empresa_id, limit=limit)


@router.post("/events/{event_id}/processing", response_model=OutboxEventResponse, dependencies=[Depends(require_permissions(["outbox.eventos.procesar"]))])
async def marcar_evento_processing(event_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await OutboxService(db).mark_processing(empresa_id=current_user.empresa_id, event_id=event_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/events/{event_id}/published", response_model=OutboxEventResponse, dependencies=[Depends(require_permissions(["outbox.eventos.procesar"]))])
async def marcar_evento_publicado(event_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await OutboxService(db).mark_published(empresa_id=current_user.empresa_id, event_id=event_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/events/{event_id}/failed", response_model=OutboxEventResponse, dependencies=[Depends(require_permissions(["outbox.eventos.procesar"]))])
async def marcar_evento_fallido(event_id: UUID, payload: OutboxEventFailRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await OutboxService(db).mark_failed(empresa_id=current_user.empresa_id, event_id=event_id, error=payload.error, retry_delay_seconds=payload.retry_delay_seconds)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
