from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.usuario import Sesion, Usuario


class SessionSecurityService:
    """Session and account-lockout controls for authentication hardening."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def revoke_user_sessions(self, *, usuario_id: UUID, except_session_id: UUID | None = None) -> int:
        query = update(Sesion).where(Sesion.usuario_id == usuario_id, Sesion.es_activa.is_(True))
        if except_session_id is not None:
            query = query.where(Sesion.id != except_session_id)
        result = await self.db.execute(query.values(es_activa=False, ultima_actividad=datetime.now(timezone.utc)))
        await self.db.flush()
        return result.rowcount or 0

    async def cleanup_expired_sessions(self, *, limit: int = 1000) -> int:
        expired = await self.db.execute(
            select(Sesion.id)
            .where(Sesion.es_activa.is_(True), Sesion.expira_en < datetime.now(timezone.utc))
            .limit(limit)
        )
        session_ids = list(expired.scalars().all())
        if not session_ids:
            return 0
        result = await self.db.execute(
            update(Sesion).where(Sesion.id.in_(session_ids)).values(es_activa=False, ultima_actividad=datetime.now(timezone.utc))
        )
        await self.db.flush()
        return result.rowcount or 0

    async def record_failed_login(self, *, usuario: Usuario) -> Usuario:
        usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
        if usuario.intentos_fallidos >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            usuario.bloqueado_hasta = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCOUNT_LOCK_MINUTES)
        await self.db.flush()
        return usuario

    async def clear_failed_logins(self, *, usuario: Usuario) -> Usuario:
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        await self.db.flush()
        return usuario
