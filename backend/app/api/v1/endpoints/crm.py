from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions, require_sucursal_scope
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.crm import CitaOpticaCreate, CitaOpticaResponse, RecordatorioClienteCreate, RecordatorioClienteResponse
from app.services.crm_service import CRMService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/citas", response_model=CitaOpticaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["crm.citas.crear"]))])
async def crear_cita(payload: CitaOpticaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    require_sucursal_scope(payload.sucursal_id, current_user)
    try:
        cita = await CRMService(db).crear_cita(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="CRM_CITA_CREAR", entidad="CitaOptica", entidad_id=cita.id, payload={"folio": cita.folio, "fecha_inicio": cita.fecha_inicio.isoformat()})
        return cita
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/citas", response_model=list[CitaOpticaResponse], dependencies=[Depends(require_permissions(["crm.citas.leer"]))])
async def listar_citas(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await CRMService(db).listar_citas(empresa_id=current_user.empresa_id, skip=skip, limit=limit)


@router.post("/citas/{cita_id}/estado/{estado}", response_model=CitaOpticaResponse, dependencies=[Depends(require_permissions(["crm.citas.estado"]))])
async def cambiar_estado_cita(cita_id: UUID, estado: str, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        cita = await CRMService(db).cambiar_estado_cita(empresa_id=current_user.empresa_id, cita_id=cita_id, estado=estado)
        await audit_user_action(db, current_user=current_user, accion="CRM_CITA_ESTADO", entidad="CitaOptica", entidad_id=cita.id, payload={"estado": cita.estado})
        return cita
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/recordatorios", response_model=RecordatorioClienteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["crm.recordatorios.crear"]))])
async def crear_recordatorio(payload: RecordatorioClienteCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        recordatorio = await CRMService(db).crear_recordatorio(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="CRM_RECORDATORIO_CREAR", entidad="RecordatorioCliente", entidad_id=recordatorio.id, payload={"tipo": recordatorio.tipo, "canal": recordatorio.canal})
        return recordatorio
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/recordatorios/pendientes", response_model=list[RecordatorioClienteResponse], dependencies=[Depends(require_permissions(["crm.recordatorios.leer"]))])
async def listar_recordatorios_pendientes(limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await CRMService(db).listar_recordatorios_pendientes(empresa_id=current_user.empresa_id, limit=limit)
