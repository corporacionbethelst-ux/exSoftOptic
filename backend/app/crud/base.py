from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=Any)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=Any)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base CRUD con métodos genéricos reutilizables.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Obtener un registro por ID"""
        result = await db.execute(
            select(self.model).where(
                and_(
                    self.model.id == UUID(id),
                    self.model.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Obtener múltiples registros con filtros y paginación"""
        query = select(self.model).where(self.model.deleted_at.is_(None))
        
        # Aplicar filtros
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        # Búsqueda
        if search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).ilike(f"%{search}%")
                    )
            if search_conditions:
                query = query.where(search_conditions[0])
                for condition in search_conditions[1:]:
                    query = query.or_(condition)
        
        # Ordenamiento
        if order_by:
            if order_by.startswith("-"):
                query = query.order_by(getattr(self.model, order_by[1:]).desc())
            else:
                query = query.order_by(getattr(self.model, order_by).asc())
        else:
            query = query.order_by(self.model.created_at.desc())
        
        # Paginación
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Contar registros"""
        query = select(func.count()).select_from(self.model).where(
            self.model.deleted_at.is_(None)
        )
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro"""
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar un registro"""
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: str, soft: bool = True) -> bool:
        """Eliminar registro (soft delete por defecto)"""
        obj = await self.get(db, id)
        if not obj:
            return False
        
        if soft:
            from datetime import datetime
            obj.deleted_at = datetime.utcnow()
        else:
            await db.delete(obj)
        
        await db.flush()
        return True
    
    async def exists(self, db: AsyncSession, **kwargs) -> bool:
        """Verificar si existe un registro"""
        query = select(func.count()).select_from(self.model).where(
            self.model.deleted_at.is_(None)
        )
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        result = await db.execute(query)
        return (result.scalar() or 0) > 0