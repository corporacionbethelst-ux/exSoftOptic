from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.inventory_accounting import ProductoCreate, ProductoResponse

router = APIRouter()

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: ProductoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    producto = Producto(**payload.model_dump(), empresa_id=current_user.empresa_id)
    db.add(producto)
    await db.flush()
    return producto

@router.get("/", response_model=dict)
async def listar_productos(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    query = select(Producto).where(Producto.empresa_id == current_user.empresa_id, Producto.deleted_at.is_(None)).offset(skip).limit(limit)
    total = await db.scalar(select(func.count()).select_from(Producto).where(Producto.empresa_id == current_user.empresa_id))
    rows = (await db.execute(query)).scalars().all()
    return {"total": total, "skip": skip, "limit": limit, "items": [ProductoResponse.model_validate(row) for row in rows]}
