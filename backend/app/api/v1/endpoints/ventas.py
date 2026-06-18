from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.ventas import VentaConfirmarRequest, VentaCreate, VentaResponse
from app.services.sales_service import SalesService

router = APIRouter()


@router.post("/", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def crear_venta(
    payload: VentaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        return await SalesService(db).crear_venta(empresa_id=current_user.empresa_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/", response_model=list[VentaResponse])
async def listar_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    return await SalesService(db).listar_ventas(empresa_id=current_user.empresa_id, skip=skip, limit=limit)


@router.get("/{venta_id}", response_model=VentaResponse)
async def obtener_venta(
    venta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        return await SalesService(db).obtener_venta(empresa_id=current_user.empresa_id, venta_id=venta_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{venta_id}/confirmar", response_model=VentaResponse)
async def confirmar_venta(
    venta_id: UUID,
    payload: VentaConfirmarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        return await SalesService(db).confirmar_venta(
            empresa_id=current_user.empresa_id,
            venta_id=venta_id,
            **payload.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
