from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.facturacion import FacturaCancelarRequest, FacturaEmitirRequest, FacturaResponse
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.post("/emitir", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def emitir_factura(payload: FacturaEmitirRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await InvoiceService(db).emitir_desde_venta(empresa_id=current_user.empresa_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{factura_id}", response_model=FacturaResponse)
async def obtener_factura(factura_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await InvoiceService(db).obtener_factura(empresa_id=current_user.empresa_id, factura_id=factura_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{factura_id}/cancelar", response_model=FacturaResponse)
async def cancelar_factura(factura_id: UUID, payload: FacturaCancelarRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await InvoiceService(db).cancelar_factura(empresa_id=current_user.empresa_id, factura_id=factura_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
