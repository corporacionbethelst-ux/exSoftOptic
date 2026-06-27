from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.tesoreria import ConciliacionBancariaResponse, ConciliarMovimientoRequest, CuentaBancariaCreate, CuentaBancariaResponse, ImportarEstadoBancarioRequest, ImportarEstadoBancarioResponse, MovimientoBancarioCreate, MovimientoBancarioResponse
from app.services.secured_audit import audit_user_action
from app.services.treasury_service import TreasuryService

router = APIRouter()


@router.post("/cuentas-bancarias", response_model=CuentaBancariaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["tesoreria.cuentas.crear"]))])
async def crear_cuenta_bancaria(payload: CuentaBancariaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        cuenta = await TreasuryService(db).crear_cuenta_bancaria(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="TESORERIA_CUENTA_CREAR", entidad="CuentaBancaria", entidad_id=cuenta.id, payload={"banco": cuenta.banco})
        return cuenta
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/movimientos", response_model=MovimientoBancarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["tesoreria.movimientos.crear"]))])
async def registrar_movimiento(payload: MovimientoBancarioCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        movimiento = await TreasuryService(db).registrar_movimiento(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="TESORERIA_MOVIMIENTO_CREAR", entidad="MovimientoBancario", entidad_id=movimiento.id, payload={"referencia": movimiento.referencia, "monto": str(movimiento.monto)})
        return movimiento
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/movimientos/importar", response_model=ImportarEstadoBancarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["tesoreria.movimientos.importar"]))])
async def importar_estado_bancario(payload: ImportarEstadoBancarioRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        movimientos, omitidos = await TreasuryService(db).importar_estado_bancario(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="TESORERIA_MOVIMIENTOS_IMPORTAR", entidad="CuentaBancaria", entidad_id=payload.cuenta_bancaria_id, payload={"importados": len(movimientos), "omitidos": omitidos, "proveedor": payload.proveedor})
        return ImportarEstadoBancarioResponse(importados=len(movimientos), omitidos=omitidos, movimientos=movimientos)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/movimientos/pendientes", response_model=list[MovimientoBancarioResponse], dependencies=[Depends(require_permissions(["tesoreria.movimientos.leer"]))])
async def movimientos_pendientes(cuenta_bancaria_id: UUID | None = Query(None), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await TreasuryService(db).listar_movimientos_pendientes(empresa_id=current_user.empresa_id, cuenta_bancaria_id=cuenta_bancaria_id, skip=skip, limit=limit)


@router.post("/conciliaciones", response_model=ConciliacionBancariaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["tesoreria.conciliar"]))])
async def conciliar_movimiento(payload: ConciliarMovimientoRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        conciliacion = await TreasuryService(db).conciliar_movimiento(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="TESORERIA_CONCILIAR", entidad="ConciliacionBancaria", entidad_id=conciliacion.id, payload={"movimiento_id": str(payload.movimiento_id), "asiento_id": str(payload.asiento_id)})
        return conciliacion
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
