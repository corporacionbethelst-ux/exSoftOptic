from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.auditoria import AuditoriaEventoResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/", response_model=list[AuditoriaEventoResponse], dependencies=[Depends(require_permissions(["auditoria.leer"]))])
async def listar_eventos_auditoria(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    return await AuditService(db).list_events(empresa_id=current_user.empresa_id, limit=limit)


@router.get("/verificar-cadena", dependencies=[Depends(require_permissions(["auditoria.verificar"]))])
async def verificar_cadena_auditoria(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    valid = await AuditService(db).verify_chain(empresa_id=current_user.empresa_id)
    return {"valid": valid}
