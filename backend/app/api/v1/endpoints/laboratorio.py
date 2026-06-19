from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.laboratorio import CompletarEtapaRequest, ConsumoMaterialCreate, ConsumoMaterialResponse, ControlCalidadCreate, OrdenLaboratorioFromVentaCreate, OrdenLaboratorioResponse
from app.services.lab_service import LabService

router = APIRouter()


@router.post("/ordenes/from-venta/{venta_id}", response_model=OrdenLaboratorioResponse, status_code=status.HTTP_201_CREATED)
async def crear_desde_venta(venta_id: UUID, payload: OrdenLaboratorioFromVentaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).crear_orden_desde_venta(empresa_id=current_user.empresa_id, venta_id=venta_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/ordenes", response_model=list[OrdenLaboratorioResponse])
async def listar_ordenes(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await LabService(db).listar_ordenes(empresa_id=current_user.empresa_id, skip=skip, limit=limit)


@router.get("/ordenes/{orden_id}", response_model=OrdenLaboratorioResponse)
async def obtener_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).obtener_orden(empresa_id=current_user.empresa_id, orden_id=orden_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/iniciar", response_model=OrdenLaboratorioResponse)
async def iniciar_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).iniciar_orden(empresa_id=current_user.empresa_id, orden_id=orden_id, responsable_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/consumos", response_model=ConsumoMaterialResponse, status_code=status.HTTP_201_CREATED)
async def registrar_consumo(orden_id: UUID, payload: ConsumoMaterialCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).registrar_consumo_material(empresa_id=current_user.empresa_id, orden_id=orden_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/etapas/{etapa_id}/completar", response_model=OrdenLaboratorioResponse)
async def completar_etapa(orden_id: UUID, etapa_id: UUID, payload: CompletarEtapaRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).completar_etapa(empresa_id=current_user.empresa_id, orden_id=orden_id, etapa_id=etapa_id, observaciones=payload.observaciones)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/control-calidad", response_model=OrdenLaboratorioResponse)
async def control_calidad(orden_id: UUID, payload: ControlCalidadCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).registrar_control_calidad(empresa_id=current_user.empresa_id, orden_id=orden_id, payload=payload, usuario_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/entregar", response_model=OrdenLaboratorioResponse)
async def entregar_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await LabService(db).entregar_orden(empresa_id=current_user.empresa_id, orden_id=orden_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
