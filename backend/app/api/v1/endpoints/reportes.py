from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.reportes import BalanzaComprobacionResponse, InventarioValuadoResponse, MargenVentasResponse
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/contabilidad/balanza", response_model=BalanzaComprobacionResponse)
async def balanza_comprobacion(fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).balanza_comprobacion(empresa_id=current_user.empresa_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/inventario/valuado", response_model=InventarioValuadoResponse)
async def inventario_valuado(sucursal_id: UUID | None = Query(None), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).inventario_valuado(empresa_id=current_user.empresa_id, sucursal_id=sucursal_id)


@router.get("/ventas/margenes", response_model=MargenVentasResponse)
async def margen_ventas(fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).margen_ventas(empresa_id=current_user.empresa_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
