from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.compras import OrdenCompraCreate, OrdenCompraResponse, RecepcionCompraCreate, RecepcionCompraResponse
from app.services.purchase_service import PurchaseService

router = APIRouter()


@router.post("/ordenes", response_model=OrdenCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear_orden(payload: OrdenCompraCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PurchaseService(db).crear_orden(empresa_id=current_user.empresa_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/aprobar", response_model=OrdenCompraResponse)
async def aprobar_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PurchaseService(db).aprobar_orden(empresa_id=current_user.empresa_id, orden_id=orden_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/ordenes/{orden_id}", response_model=OrdenCompraResponse)
async def obtener_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PurchaseService(db).obtener_orden(empresa_id=current_user.empresa_id, orden_id=orden_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/recepciones", response_model=RecepcionCompraResponse, status_code=status.HTTP_201_CREATED)
async def recibir_orden(orden_id: UUID, payload: RecepcionCompraCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PurchaseService(db).recibir_orden(empresa_id=current_user.empresa_id, orden_id=orden_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
