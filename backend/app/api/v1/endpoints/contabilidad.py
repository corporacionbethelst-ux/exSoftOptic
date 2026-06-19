from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.contabilidad import AsientoContable, CuentaContable
from app.models.usuario import Usuario
from app.schemas.inventory_accounting import AsientoResponse, CuentaContableCreate, CuentaContableResponse

router = APIRouter()

@router.post("/cuentas", response_model=CuentaContableResponse, status_code=status.HTTP_201_CREATED)
async def crear_cuenta(payload: CuentaContableCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    cuenta = CuentaContable(**payload.model_dump(), empresa_id=current_user.empresa_id)
    db.add(cuenta)
    await db.flush()
    return cuenta

@router.get("/cuentas", response_model=list[CuentaContableResponse])
async def listar_cuentas(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(CuentaContable).where(CuentaContable.empresa_id == current_user.empresa_id).order_by(CuentaContable.codigo).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/asientos", response_model=list[AsientoResponse])
async def listar_asientos(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    result = await db.execute(select(AsientoContable).options(selectinload(AsientoContable.lineas)).where(AsientoContable.empresa_id == current_user.empresa_id).order_by(AsientoContable.fecha.desc(), AsientoContable.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()
