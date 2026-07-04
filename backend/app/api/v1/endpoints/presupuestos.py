from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.presupuestos import CentroCostoCreate, CentroCostoResponse, ComprometerPresupuestoRequest, PresupuestoCreate, PresupuestoResponse
from app.services.budget_service import BudgetService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/centros-costo", response_model=CentroCostoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["presupuestos.centros_costo.crear"]))])
async def crear_centro_costo(payload: CentroCostoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    centro = await BudgetService(db).crear_centro_costo(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="PRESUPUESTO_CENTRO_COSTO_CREAR", entidad="CentroCosto", entidad_id=centro.id, payload={"codigo": centro.codigo})
    return centro


@router.post("/", response_model=PresupuestoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["presupuestos.crear"]))])
async def crear_presupuesto(payload: PresupuestoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        presupuesto = await BudgetService(db).crear_presupuesto(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="PRESUPUESTO_CREAR", entidad="Presupuesto", entidad_id=presupuesto.id, payload={"folio": presupuesto.folio})
        return presupuesto
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/comprometer", response_model=PresupuestoResponse, dependencies=[Depends(require_permissions(["presupuestos.comprometer"]))])
async def comprometer_presupuesto(payload: ComprometerPresupuestoRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        presupuesto = await BudgetService(db).comprometer(empresa_id=current_user.empresa_id, payload=payload)
        await audit_user_action(db, current_user=current_user, accion="PRESUPUESTO_COMPROMETER", entidad="Presupuesto", entidad_id=presupuesto.id, payload={"cuenta_codigo": payload.cuenta_codigo, "monto": str(payload.monto)})
        return presupuesto
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
