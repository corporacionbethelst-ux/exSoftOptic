from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.inventario import KardexMovimiento
from app.models.usuario import Usuario
from app.schemas.inventory_accounting import InventarioEntradaRequest, InventarioSalidaRequest, KardexResponse
from app.services.inventory_service import InventoryService

router = APIRouter()

@router.post("/entradas", response_model=KardexResponse, status_code=status.HTTP_201_CREATED)
async def registrar_entrada(payload: InventarioEntradaRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await InventoryService(db).entrada(empresa_id=current_user.empresa_id, **payload.model_dump())

@router.post("/salidas", response_model=KardexResponse, status_code=status.HTTP_201_CREATED)
async def registrar_salida(payload: InventarioSalidaRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    movimiento, _ = await InventoryService(db).salida_peps(empresa_id=current_user.empresa_id, **payload.model_dump())
    return movimiento

@router.get("/kardex", response_model=list[KardexResponse])
async def kardex(producto_id: str | None = None, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    query = select(KardexMovimiento).where(KardexMovimiento.empresa_id == current_user.empresa_id).order_by(KardexMovimiento.created_at.desc()).offset(skip).limit(limit)
    if producto_id:
        query = query.where(KardexMovimiento.producto_id == producto_id)
    return (await db.execute(query)).scalars().all()
