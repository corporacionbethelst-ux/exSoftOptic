from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.contabilidad import AsientoContable, CuentaContable
from app.models.usuario import Usuario
from app.schemas.inventory_accounting import AsientoResponse, CuentaContableCreate, CuentaContableResponse, PeriodoContableCreate, PeriodoContableEstadoRequest, PeriodoContableResponse
from app.services.accounting_period_service import AccountingPeriodService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/cuentas", response_model=CuentaContableResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["contabilidad.cuentas.crear"]))])
async def crear_cuenta(payload: CuentaContableCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    cuenta = CuentaContable(**payload.model_dump(), empresa_id=current_user.empresa_id)
    db.add(cuenta)
    await db.flush()
    return cuenta


@router.get("/cuentas", response_model=list[CuentaContableResponse], dependencies=[Depends(require_permissions(["contabilidad.cuentas.leer"]))])
async def listar_cuentas(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(CuentaContable).where(CuentaContable.empresa_id == current_user.empresa_id).order_by(CuentaContable.codigo).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/asientos", response_model=list[AsientoResponse], dependencies=[Depends(require_permissions(["contabilidad.asientos.leer"]))])
async def listar_asientos(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(AsientoContable).options(selectinload(AsientoContable.lineas)).where(AsientoContable.empresa_id == current_user.empresa_id).order_by(AsientoContable.fecha.desc(), AsientoContable.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/periodos", response_model=PeriodoContableResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["contabilidad.periodos.crear"]))])
async def crear_periodo_contable(payload: PeriodoContableCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        periodo = await AccountingPeriodService(db).crear_periodo(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="CONTABILIDAD_PERIODO_CREAR", entidad="PeriodoContable", entidad_id=periodo.id, payload={"codigo": periodo.codigo, "fecha_inicio": str(periodo.fecha_inicio), "fecha_fin": str(periodo.fecha_fin)})
        return periodo
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/periodos", response_model=list[PeriodoContableResponse], dependencies=[Depends(require_permissions(["contabilidad.periodos.leer"]))])
async def listar_periodos_contables(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await AccountingPeriodService(db).listar_periodos(empresa_id=current_user.empresa_id, skip=skip, limit=limit)


@router.patch("/periodos/{periodo_id}/estado", response_model=PeriodoContableResponse, dependencies=[Depends(require_permissions(["contabilidad.periodos.cerrar"]))])
async def cambiar_estado_periodo_contable(periodo_id: UUID, payload: PeriodoContableEstadoRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        periodo = await AccountingPeriodService(db).cambiar_estado(empresa_id=current_user.empresa_id, periodo_id=periodo_id, estado=payload.estado)
        await audit_user_action(db, current_user=current_user, accion="CONTABILIDAD_PERIODO_ESTADO", entidad="PeriodoContable", entidad_id=periodo.id, payload={"codigo": periodo.codigo, "estado": periodo.estado})
        return periodo
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
