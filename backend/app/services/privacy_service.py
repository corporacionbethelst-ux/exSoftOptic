from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import CitaOptica, RecordatorioCliente
from app.models.venta import Cliente, Paciente, RecetaOptica, Venta


def json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    return value


def record(model: Any, fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: json_value(getattr(model, field)) for field in fields}


class PrivacyService:
    """Tenant-scoped subject access and direct-identifier anonymization."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_subject(self, *, empresa_id: UUID, cliente_id: UUID) -> dict[str, Any]:
        cliente = await self._get_cliente(empresa_id, cliente_id)
        pacientes = await self._list(Paciente, empresa_id, Paciente.cliente_id == cliente_id)
        patient_ids = [paciente.id for paciente in pacientes]
        recetas = (
            await self._list(RecetaOptica, empresa_id, RecetaOptica.paciente_id.in_(patient_ids))
            if patient_ids
            else []
        )
        ventas = await self._list(Venta, empresa_id, Venta.cliente_id == cliente_id)
        citas = await self._list(CitaOptica, empresa_id, CitaOptica.cliente_id == cliente_id)
        recordatorios = await self._list(
            RecordatorioCliente, empresa_id, RecordatorioCliente.cliente_id == cliente_id
        )
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cliente": record(
                cliente,
                ("id", "nombre", "email", "telefono", "rfc", "codigo_postal", "regimen_fiscal", "created_at", "updated_at"),
            ),
            "pacientes": [
                record(item, ("id", "cliente_id", "nombre", "fecha_nacimiento", "telefono", "email", "created_at"))
                for item in pacientes
            ],
            "recetas": [
                record(
                    item,
                    (
                        "id", "paciente_id", "fecha", "od_esfera", "od_cilindro", "od_eje",
                        "od_adicion", "oi_esfera", "oi_cilindro", "oi_eje", "oi_adicion",
                        "dnp", "altura", "observaciones", "created_at",
                    ),
                )
                for item in recetas
            ],
            "ventas": [record(item, ("id", "folio", "fecha", "estado", "subtotal", "impuestos", "total")) for item in ventas],
            "citas": [record(item, ("id", "folio", "fecha_inicio", "fecha_fin", "tipo", "estado", "motivo", "observaciones")) for item in citas],
            "recordatorios": [record(item, ("id", "tipo", "canal", "programado_para", "estado", "mensaje")) for item in recordatorios],
        }

    async def anonymize_subject(self, *, empresa_id: UUID, cliente_id: UUID) -> dict[str, Any]:
        cliente = await self._get_cliente(empresa_id, cliente_id)
        now = datetime.now(timezone.utc)
        pacientes = await self._list(Paciente, empresa_id, Paciente.cliente_id == cliente_id)
        patient_ids = [paciente.id for paciente in pacientes]
        recetas = (
            await self._list(RecetaOptica, empresa_id, RecetaOptica.paciente_id.in_(patient_ids))
            if patient_ids
            else []
        )
        citas = await self._list(CitaOptica, empresa_id, CitaOptica.cliente_id == cliente_id)
        recordatorios = await self._list(
            RecordatorioCliente, empresa_id, RecordatorioCliente.cliente_id == cliente_id
        )

        cliente.nombre = f"ANONIMIZADO-{str(cliente.id)[:8]}"
        cliente.email = None
        cliente.telefono = None
        cliente.rfc = None
        cliente.codigo_postal = None
        cliente.regimen_fiscal = None
        cliente.deleted_at = now
        cliente.is_active = False
        for paciente in pacientes:
            paciente.nombre = f"ANONIMIZADO-{str(paciente.id)[:8]}"
            paciente.fecha_nacimiento = None
            paciente.telefono = None
            paciente.email = None
            paciente.deleted_at = now
            paciente.is_active = False
        for receta in recetas:
            receta.observaciones = None
        for cita in citas:
            cita.motivo = "DATOS_RESTRINGIDOS"
            cita.observaciones = None
        for reminder in recordatorios:
            reminder.mensaje = "DATOS_RESTRINGIDOS"
            if reminder.estado == "PENDIENTE":
                reminder.estado = "CANCELADO"
        await self.db.flush()
        return {
            "cliente_id": str(cliente.id),
            "anonymized_at": now.isoformat(),
            "patients_anonymized": len(pacientes),
            "prescriptions_redacted": len(recetas),
            "appointments_redacted": len(citas),
            "reminders_redacted": len(recordatorios),
        }

    async def _get_cliente(self, empresa_id: UUID, cliente_id: UUID) -> Cliente:
        result = await self.db.execute(
            select(Cliente).where(Cliente.empresa_id == empresa_id, Cliente.id == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        if cliente is None:
            raise ValueError("Cliente inexistente para la empresa")
        return cliente

    async def _list(self, model: Any, empresa_id: UUID, condition: Any) -> list[Any]:
        result = await self.db.execute(
            select(model).where(model.empresa_id == empresa_id, condition)
        )
        return list(result.scalars().all())
