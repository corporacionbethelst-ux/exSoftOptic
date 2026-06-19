from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.nomina import EmpleadoCreate, EmpleadoResponse, NominaConfirmarRequest, NominaPeriodoCreate, NominaPeriodoResponse
from app.services.payroll_service import PayrollService

router = APIRouter()


@router.post("/empleados", response_model=EmpleadoResponse, status_code=status.HTTP_201_CREATED)
async def crear_empleado(payload: EmpleadoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await PayrollService(db).crear_empleado(empresa_id=current_user.empresa_id, payload=payload)


@router.post("/periodos", response_model=NominaPeriodoResponse, status_code=status.HTTP_201_CREATED)
async def crear_periodo(payload: NominaPeriodoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PayrollService(db).crear_periodo(empresa_id=current_user.empresa_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/periodos/{periodo_id}/calcular", response_model=NominaPeriodoResponse)
async def calcular_periodo(periodo_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PayrollService(db).calcular_periodo(empresa_id=current_user.empresa_id, periodo_id=periodo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/periodos/{periodo_id}/confirmar", response_model=NominaPeriodoResponse)
async def confirmar_periodo(periodo_id: UUID, payload: NominaConfirmarRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PayrollService(db).confirmar_periodo(empresa_id=current_user.empresa_id, periodo_id=periodo_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/periodos/{periodo_id}", response_model=NominaPeriodoResponse)
async def obtener_periodo(periodo_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await PayrollService(db).obtener_periodo(empresa_id=current_user.empresa_id, periodo_id=periodo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
