import hashlib
import json
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditoria import AuditoriaEvento
from app.schemas.auditoria import AuditoriaEventoCreate


@dataclass(frozen=True)
class AuditChainVerification:
    valid: bool
    total_events: int
    first_invalid_sequence: int | None = None
    reason: str | None = None
    last_hash: str | None = None


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_event(
        self,
        *,
        empresa_id: UUID | None,
        usuario_id: UUID | None,
        payload: AuditoriaEventoCreate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditoriaEvento:
        last_sequence, previous_hash = await self._last_event(empresa_id)
        secuencia = last_sequence + 1
        event_hash = self._hash_event(
            empresa_id=str(empresa_id) if empresa_id else None,
            usuario_id=str(usuario_id) if usuario_id else None,
            secuencia=secuencia,
            accion=payload.accion,
            entidad=payload.entidad,
            entidad_id=payload.entidad_id,
            payload=payload.payload,
            previous_hash=previous_hash,
        )
        evento = AuditoriaEvento(
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            secuencia=secuencia,
            accion=payload.accion,
            entidad=payload.entidad,
            entidad_id=payload.entidad_id,
            ip_address=ip_address,
            user_agent=user_agent,
            payload=payload.payload,
            previous_hash=previous_hash,
            event_hash=event_hash,
            descripcion=payload.descripcion,
        )
        self.db.add(evento)
        await self.db.flush()
        return evento

    async def list_events(self, *, empresa_id: UUID, limit: int = 100) -> list[AuditoriaEvento]:
        result = await self.db.execute(
            select(AuditoriaEvento)
            .where(AuditoriaEvento.empresa_id == empresa_id)
            .order_by(AuditoriaEvento.secuencia.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def verify_chain(self, *, empresa_id: UUID) -> bool:
        verification = await self.verify_chain_details(empresa_id=empresa_id)
        return verification.valid

    async def verify_chain_details(self, *, empresa_id: UUID) -> AuditChainVerification:
        result = await self.db.execute(
            select(AuditoriaEvento)
            .where(AuditoriaEvento.empresa_id == empresa_id)
            .order_by(AuditoriaEvento.secuencia.asc())
        )
        previous_hash = None
        expected_sequence = 1
        total_events = 0
        for evento in result.scalars().all():
            total_events += 1
            expected = self._hash_event(
                empresa_id=str(evento.empresa_id) if evento.empresa_id else None,
                usuario_id=str(evento.usuario_id) if evento.usuario_id else None,
                secuencia=evento.secuencia,
                accion=evento.accion,
                entidad=evento.entidad,
                entidad_id=evento.entidad_id,
                payload=evento.payload,
                previous_hash=previous_hash,
            )
            if evento.secuencia != expected_sequence:
                return AuditChainVerification(
                    valid=False,
                    total_events=total_events,
                    first_invalid_sequence=evento.secuencia,
                    reason=f"secuencia esperada {expected_sequence} y recibida {evento.secuencia}",
                    last_hash=previous_hash,
                )
            if evento.previous_hash != previous_hash:
                return AuditChainVerification(
                    valid=False,
                    total_events=total_events,
                    first_invalid_sequence=evento.secuencia,
                    reason="previous_hash no coincide con el hash del evento anterior",
                    last_hash=previous_hash,
                )
            if evento.event_hash != expected:
                return AuditChainVerification(
                    valid=False,
                    total_events=total_events,
                    first_invalid_sequence=evento.secuencia,
                    reason="event_hash no coincide con el contenido del evento",
                    last_hash=previous_hash,
                )
            previous_hash = evento.event_hash
            expected_sequence += 1
        return AuditChainVerification(valid=True, total_events=total_events, last_hash=previous_hash)

    async def _last_event(self, empresa_id: UUID | None) -> tuple[int, str | None]:
        query = select(AuditoriaEvento.secuencia, AuditoriaEvento.event_hash).order_by(AuditoriaEvento.secuencia.desc()).limit(1)
        if empresa_id:
            query = query.where(AuditoriaEvento.empresa_id == empresa_id)
        result = await self.db.execute(query)
        row = result.one_or_none()
        if row is None:
            return 0, None
        return row.secuencia, row.event_hash

    def _hash_event(self, **data) -> str:
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
