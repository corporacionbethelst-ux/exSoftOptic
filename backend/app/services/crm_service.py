from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import CitaOptica, RecordatorioCliente
from app.models.sucursal import Sucursal
from app.models.usuario import Usuario
from app.models.venta import Cliente, Paciente
from app.schemas.crm import CitaOpticaCreate, RecordatorioClienteCreate


class CRMService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_cita(self, *, empresa_id: UUID, payload: CitaOpticaCreate) -> CitaOptica:
        await self._validar_sucursal(empresa_id, payload.sucursal_id)
        await self._validar_cliente(empresa_id, payload.cliente_id)
        if payload.paciente_id:
            await self._validar_paciente(empresa_id, payload.paciente_id, payload.cliente_id)
        if payload.optometrista_id:
            await self._validar_usuario(empresa_id, payload.optometrista_id)
        cita = CitaOptica(empresa_id=empresa_id, estado="PROGRAMADA", **payload.model_dump())
        self.db.add(cita)
        await self.db.flush()
        return cita

    async def listar_citas(self, *, empresa_id: UUID, skip: int = 0, limit: int = 50) -> list[CitaOptica]:
        result = await self.db.execute(
            select(CitaOptica)
            .where(CitaOptica.empresa_id == empresa_id)
            .order_by(CitaOptica.fecha_inicio.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def cambiar_estado_cita(self, *, empresa_id: UUID, cita_id: UUID, estado: str) -> CitaOptica:
        result = await self.db.execute(select(CitaOptica).where(CitaOptica.empresa_id == empresa_id, CitaOptica.id == cita_id).with_for_update())
        cita = result.scalar_one_or_none()
        if cita is None:
            raise ValueError("Cita inexistente")
        if estado not in {"PROGRAMADA", "CONFIRMADA", "EN_PROCESO", "COMPLETADA", "CANCELADA", "NO_ASISTIO"}:
            raise ValueError("Estado de cita inválido")
        cita.estado = estado
        await self.db.flush()
        return cita

    async def crear_recordatorio(self, *, empresa_id: UUID, payload: RecordatorioClienteCreate) -> RecordatorioCliente:
        await self._validar_cliente(empresa_id, payload.cliente_id)
        if payload.paciente_id:
            await self._validar_paciente(empresa_id, payload.paciente_id, payload.cliente_id)
        if payload.cita_id:
            cita = await self.db.get(CitaOptica, payload.cita_id)
            if cita is None or cita.empresa_id != empresa_id or cita.cliente_id != payload.cliente_id:
                raise ValueError("Cita inexistente para el cliente")
        recordatorio = RecordatorioCliente(empresa_id=empresa_id, estado="PENDIENTE", **payload.model_dump())
        self.db.add(recordatorio)
        await self.db.flush()
        return recordatorio

    async def listar_recordatorios_pendientes(self, *, empresa_id: UUID, limit: int = 100) -> list[RecordatorioCliente]:
        result = await self.db.execute(
            select(RecordatorioCliente)
            .where(RecordatorioCliente.empresa_id == empresa_id, RecordatorioCliente.estado == "PENDIENTE")
            .order_by(RecordatorioCliente.programado_para.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def _validar_sucursal(self, empresa_id: UUID, sucursal_id: UUID) -> None:
        sucursal = await self.db.get(Sucursal, sucursal_id)
        if sucursal is None or sucursal.empresa_id != empresa_id:
            raise ValueError("Sucursal inexistente para la empresa")

    async def _validar_cliente(self, empresa_id: UUID, cliente_id: UUID) -> None:
        cliente = await self.db.get(Cliente, cliente_id)
        if cliente is None or cliente.empresa_id != empresa_id:
            raise ValueError("Cliente inexistente para la empresa")

    async def _validar_paciente(self, empresa_id: UUID, paciente_id: UUID, cliente_id: UUID) -> None:
        paciente = await self.db.get(Paciente, paciente_id)
        if paciente is None or paciente.empresa_id != empresa_id or paciente.cliente_id != cliente_id:
            raise ValueError("Paciente inexistente para el cliente")

    async def _validar_usuario(self, empresa_id: UUID, usuario_id: UUID) -> None:
        usuario = await self.db.get(Usuario, usuario_id)
        if usuario is None or usuario.empresa_id != empresa_id:
            raise ValueError("Usuario inexistente para la empresa")
