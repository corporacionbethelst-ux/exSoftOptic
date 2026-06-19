from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.compras import OrdenCompraCreate, OrdenCompraResponse, RecepcionCompraCreate, RecepcionCompraResponse
from app.services.purchase_service import PurchaseService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/ordenes", response_model=OrdenCompraResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["compras.crear"]))])
async def crear_orden(payload: OrdenCompraCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        orden = await PurchaseService(db).crear_orden(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="COMPRA_ORDEN_CREAR", entidad="OrdenCompra", entidad_id=orden.id, payload={"folio": orden.folio, "total": str(orden.total)})
        return orden
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/aprobar", response_model=OrdenCompraResponse, dependencies=[Depends(require_permissions(["compras.aprobar"]))])
async def aprobar_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        orden = await PurchaseService(db).aprobar_orden(empresa_id=current_user.empresa_id, orden_id=orden_id)
        await audit_user_action(db, current_user=current_user, accion="COMPRA_ORDEN_APROBAR", entidad="OrdenCompra", entidad_id=orden.id, payload={"folio": orden.folio})
        return orden
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/ordenes/{orden_id}", response_model=OrdenCompraResponse, dependencies=[Depends(require_permissions(["compras.leer"]))])
async def obtener_orden(orden_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PurchaseService(db).obtener_orden(empresa_id=current_user.empresa_id, orden_id=orden_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/ordenes/{orden_id}/recepciones", response_model=RecepcionCompraResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["compras.recibir"]))])
async def recibir_orden(orden_id: UUID, payload: RecepcionCompraCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        recepcion = await PurchaseService(db).recibir_orden(empresa_id=current_user.empresa_id, orden_id=orden_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="COMPRA_RECEPCION_REGISTRAR", entidad="RecepcionCompra", entidad_id=recepcion.id, payload={"folio": recepcion.folio, "total": str(recepcion.total)})
        return recepcion
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
