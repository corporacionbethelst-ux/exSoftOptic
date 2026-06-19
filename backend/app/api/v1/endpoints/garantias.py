from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.garantias import GarantiaCreate, GarantiaFromOrdenCreate, GarantiaResponse, ReclamacionGarantiaCreate, ReclamacionGarantiaResponse, ResolverReclamacionRequest
from app.services.warranty_service import WarrantyService

router = APIRouter()


@router.post("/", response_model=GarantiaResponse, status_code=status.HTTP_201_CREATED)
async def crear_garantia(payload: GarantiaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await WarrantyService(db).crear_garantia(empresa_id=current_user.empresa_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/from-laboratorio/{orden_id}", response_model=GarantiaResponse, status_code=status.HTTP_201_CREATED)
async def crear_desde_laboratorio(orden_id: UUID, payload: GarantiaFromOrdenCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await WarrantyService(db).crear_desde_orden_laboratorio(empresa_id=current_user.empresa_id, orden_id=orden_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{garantia_id}", response_model=GarantiaResponse)
async def obtener_garantia(garantia_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await WarrantyService(db).obtener_garantia(empresa_id=current_user.empresa_id, garantia_id=garantia_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{garantia_id}/reclamaciones", response_model=ReclamacionGarantiaResponse, status_code=status.HTTP_201_CREATED)
async def abrir_reclamacion(garantia_id: UUID, payload: ReclamacionGarantiaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await WarrantyService(db).abrir_reclamacion(empresa_id=current_user.empresa_id, garantia_id=garantia_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/reclamaciones/{reclamacion_id}/resolver", response_model=GarantiaResponse)
async def resolver_reclamacion(reclamacion_id: UUID, payload: ResolverReclamacionRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await WarrantyService(db).resolver_reclamacion(empresa_id=current_user.empresa_id, reclamacion_id=reclamacion_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
