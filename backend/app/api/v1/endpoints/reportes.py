from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.reportes import BalanceGeneralResponse, BalanzaComprobacionResponse, EstadoResultadosResponse, InventarioValuadoResponse, LibroDiarioResponse, LibroMayorResponse, MargenVentasResponse
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/contabilidad/balanza", response_model=BalanzaComprobacionResponse, dependencies=[Depends(require_permissions(["reportes.contabilidad.leer"]))])
async def balanza_comprobacion(fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).balanza_comprobacion(empresa_id=current_user.empresa_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/contabilidad/diario", response_model=LibroDiarioResponse, dependencies=[Depends(require_permissions(["reportes.contabilidad.leer"]))])
async def libro_diario(fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).libro_diario(empresa_id=current_user.empresa_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/contabilidad/mayor", response_model=LibroMayorResponse, dependencies=[Depends(require_permissions(["reportes.contabilidad.leer"]))])
async def libro_mayor(cuenta_codigo: str | None = Query(None, max_length=40), fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).libro_mayor(empresa_id=current_user.empresa_id, cuenta_codigo=cuenta_codigo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)




@router.get("/contabilidad/estado-resultados", response_model=EstadoResultadosResponse, dependencies=[Depends(require_permissions(["reportes.contabilidad.leer"]))])
async def estado_resultados(fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).estado_resultados(empresa_id=current_user.empresa_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/contabilidad/balance-general", response_model=BalanceGeneralResponse, dependencies=[Depends(require_permissions(["reportes.contabilidad.leer"]))])
async def balance_general(fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).balance_general(empresa_id=current_user.empresa_id, fecha_fin=fecha_fin)

@router.get("/inventario/valuado", response_model=InventarioValuadoResponse, dependencies=[Depends(require_permissions(["reportes.inventario.leer"]))])
async def inventario_valuado(sucursal_id: UUID | None = Query(None), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).inventario_valuado(empresa_id=current_user.empresa_id, sucursal_id=sucursal_id)


@router.get("/ventas/margenes", response_model=MargenVentasResponse, dependencies=[Depends(require_permissions(["reportes.ventas.leer"]))])
async def margen_ventas(fecha_inicio: date | None = None, fecha_fin: date | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ReportService(db).margen_ventas(empresa_id=current_user.empresa_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
