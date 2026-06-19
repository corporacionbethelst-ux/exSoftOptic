from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions, require_sucursal_scope
from app.core.database import get_db
from app.models.inventario import KardexMovimiento
from app.models.usuario import Usuario
from app.schemas.inventory_accounting import InventarioAlertaResponse, InventarioEntradaRequest, InventarioSalidaRequest, KardexResponse
from app.services.inventory_alert_service import InventoryAlertService
from app.services.inventory_service import InventoryService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/entradas", response_model=KardexResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["inventario.entrada"]))])
async def registrar_entrada(payload: InventarioEntradaRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    require_sucursal_scope(payload.sucursal_id, current_user)
    movimiento = await InventoryService(db).entrada(empresa_id=current_user.empresa_id, **payload.model_dump())
    await audit_user_action(
        db,
        current_user=current_user,
        accion="INVENTARIO_ENTRADA",
        entidad="KardexMovimiento",
        entidad_id=movimiento.id,
        payload={"producto_id": str(payload.producto_id), "cantidad": str(payload.cantidad), "sucursal_id": str(payload.sucursal_id)},
    )
    return movimiento


@router.post("/salidas", response_model=KardexResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["inventario.salida"]))])
async def registrar_salida(payload: InventarioSalidaRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    require_sucursal_scope(payload.sucursal_id, current_user)
    movimiento, _ = await InventoryService(db).salida_peps(empresa_id=current_user.empresa_id, **payload.model_dump())
    await audit_user_action(
        db,
        current_user=current_user,
        accion="INVENTARIO_SALIDA",
        entidad="KardexMovimiento",
        entidad_id=movimiento.id,
        payload={"producto_id": str(payload.producto_id), "cantidad": str(payload.cantidad), "sucursal_id": str(payload.sucursal_id)},
    )
    return movimiento


@router.get("/kardex", response_model=list[KardexResponse], dependencies=[Depends(require_permissions(["inventario.leer"]))])
async def kardex(producto_id: str | None = None, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    query = select(KardexMovimiento).where(KardexMovimiento.empresa_id == current_user.empresa_id).order_by(KardexMovimiento.created_at.desc()).offset(skip).limit(limit)
    if producto_id:
        query = query.where(KardexMovimiento.producto_id == producto_id)
    return (await db.execute(query)).scalars().all()


@router.get("/alertas/stock-minimo", response_model=list[InventarioAlertaResponse], dependencies=[Depends(require_permissions(["inventario.alertas.leer"]))])
async def alertas_stock_minimo(sucursal_id: UUID | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await InventoryAlertService(db).alertas_stock_minimo(empresa_id=current_user.empresa_id, sucursal_id=sucursal_id)
