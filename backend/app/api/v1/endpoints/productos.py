from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.inventory_accounting import ProductoCreate, ProductoResponse, ProductoUpdate
from app.services.secured_audit import audit_user_action

router = APIRouter()


async def _get_producto_or_404(db: AsyncSession, *, empresa_id: UUID, producto_id: UUID) -> Producto:
    producto = await db.get(Producto, producto_id)
    if producto is None or producto.empresa_id != empresa_id or producto.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto inexistente")
    return producto


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["productos.crear"]))])
async def crear_producto(payload: ProductoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    producto = Producto(**payload.model_dump(), empresa_id=current_user.empresa_id)
    db.add(producto)
    await db.flush()
    await audit_user_action(
        db,
        current_user=current_user,
        accion="PRODUCTO_CREAR",
        entidad="Producto",
        entidad_id=producto.id,
        payload={"sku": producto.sku, "nombre": producto.nombre},
    )
    return producto


@router.get("/", response_model=dict, dependencies=[Depends(require_permissions(["productos.leer"]))])
async def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None, min_length=1, max_length=80),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    filters = [Producto.empresa_id == current_user.empresa_id, Producto.deleted_at.is_(None)]
    if search:
        term = f"%{search.strip()}%"
        filters.append(Producto.nombre.ilike(term) | Producto.sku.ilike(term))

    query = select(Producto).where(*filters).order_by(Producto.nombre.asc()).offset(skip).limit(limit)
    total = await db.scalar(select(func.count()).select_from(Producto).where(*filters))
    rows = (await db.execute(query)).scalars().all()
    return {"total": total, "skip": skip, "limit": limit, "items": [ProductoResponse.model_validate(row) for row in rows]}


@router.get("/{producto_id}", response_model=ProductoResponse, dependencies=[Depends(require_permissions(["productos.leer"]))])
async def obtener_producto(producto_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await _get_producto_or_404(db, empresa_id=current_user.empresa_id, producto_id=producto_id)


@router.patch("/{producto_id}", response_model=ProductoResponse, dependencies=[Depends(require_permissions(["productos.editar"]))])
async def actualizar_producto(producto_id: UUID, payload: ProductoUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    producto = await _get_producto_or_404(db, empresa_id=current_user.empresa_id, producto_id=producto_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(producto, field, value)
    await db.flush()
    await audit_user_action(
        db,
        current_user=current_user,
        accion="PRODUCTO_ACTUALIZAR",
        entidad="Producto",
        entidad_id=producto.id,
        payload={"campos": sorted(changes)},
    )
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_permissions(["productos.eliminar"]))])
async def eliminar_producto(producto_id: UUID, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    producto = await _get_producto_or_404(db, empresa_id=current_user.empresa_id, producto_id=producto_id)
    producto.deleted_at = datetime.now(timezone.utc)
    producto.is_active = False
    await db.flush()
    await audit_user_action(
        db,
        current_user=current_user,
        accion="PRODUCTO_ELIMINAR",
        entidad="Producto",
        entidad_id=producto.id,
        payload={"sku": producto.sku, "nombre": producto.nombre},
    )
    return {"message": "Producto eliminado correctamente"}
