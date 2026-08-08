from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions, require_sucursal_scope
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.crm import CitaOpticaCreate, CitaOpticaResponse, RecordatorioClienteCreate, RecordatorioClienteResponse
from app.schemas.ventas import ClienteCreate, ClienteResponse, PacienteCreate, PacienteResponse, RecetaOpticaCreate, RecetaOpticaResponse
from app.services.crm_service import CRMService
from app.services.secured_audit import audit_user_action
from app.schemas.privacy import SubjectAnonymizeRequest, SubjectAnonymizeResponse
from app.services.privacy_service import PrivacyService

router = APIRouter()


@router.get("/privacy/clientes/{cliente_id}/export", dependencies=[Depends(require_permissions(["privacidad.solicitudes.exportar"]))])
async def exportar_datos_personales(
    cliente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        export = await PrivacyService(db).export_subject(
            empresa_id=current_user.empresa_id, cliente_id=cliente_id
        )
        await audit_user_action(
            db,
            current_user=current_user,
            accion="PRIVACIDAD_EXPORTAR",
            entidad="Cliente",
            entidad_id=cliente_id,
            payload={"sections": sorted(export.keys())},
        )
        return export
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/privacy/clientes/{cliente_id}/anonymize",
    response_model=SubjectAnonymizeResponse,
    dependencies=[Depends(require_permissions(["privacidad.solicitudes.anonimizar"]))],
)
async def anonimizar_datos_personales(
    cliente_id: UUID,
    payload: SubjectAnonymizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        result = await PrivacyService(db).anonymize_subject(
            empresa_id=current_user.empresa_id, cliente_id=cliente_id
        )
        await audit_user_action(
            db,
            current_user=current_user,
            accion="PRIVACIDAD_ANONIMIZAR",
            entidad="Cliente",
            entidad_id=cliente_id,
            payload={"reason": payload.reason, **result},
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/clientes", response_model=list[ClienteResponse], dependencies=[Depends(require_permissions(["crm.clientes.leer"]))])
async def listar_clientes(
    search: str | None = Query(None, min_length=1, max_length=120),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    return await CRMService(db).listar_clientes(empresa_id=current_user.empresa_id, search=search, skip=skip, limit=limit)


@router.post("/clientes", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["crm.clientes.crear"]))])
async def crear_cliente(payload: ClienteCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    cliente = await CRMService(db).crear_cliente(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="CRM_CLIENTE_CREAR", entidad="Cliente", entidad_id=cliente.id, payload={"nombre": cliente.nombre, "email": cliente.email})
    return cliente


@router.get("/pacientes", response_model=list[PacienteResponse], dependencies=[Depends(require_permissions(["crm.pacientes.leer"]))])
async def listar_pacientes(
    cliente_id: UUID | None = None,
    search: str | None = Query(None, min_length=1, max_length=120),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    return await CRMService(db).listar_pacientes(empresa_id=current_user.empresa_id, cliente_id=cliente_id, search=search, skip=skip, limit=limit)


@router.post("/pacientes", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["crm.pacientes.crear"]))])
async def crear_paciente(payload: PacienteCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        paciente = await CRMService(db).crear_paciente(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="CRM_PACIENTE_CREAR", entidad="Paciente", entidad_id=paciente.id, payload={"nombre": paciente.nombre, "cliente_id": str(paciente.cliente_id)})
        return paciente
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/recetas", response_model=list[RecetaOpticaResponse], dependencies=[Depends(require_permissions(["crm.recetas.leer"]))])
async def listar_recetas(
    paciente_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    return await CRMService(db).listar_recetas(empresa_id=current_user.empresa_id, paciente_id=paciente_id, skip=skip, limit=limit)


@router.post("/recetas", response_model=RecetaOpticaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["crm.recetas.crear"]))])
async def crear_receta(payload: RecetaOpticaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        receta = await CRMService(db).crear_receta(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="CRM_RECETA_CREAR", entidad="RecetaOptica", entidad_id=receta.id, payload={"paciente_id": str(receta.paciente_id), "fecha": receta.fecha.isoformat()})
        return receta
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


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
