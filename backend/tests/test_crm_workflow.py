import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.empresa import Empresa
from app.models.sucursal import Sucursal
from app.models.venta import Cliente, Paciente
from app.schemas.crm import CitaOpticaCreate, RecordatorioClienteCreate
from app.services.crm_service import CRMService


@pytest.mark.asyncio
async def test_crm_crea_cita_y_recordatorio_pendiente(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="CRM Test SA", rfc="CRM260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="CRM", nombre="CRM")
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente CRM", email="crm@example.com")
    paciente = Paciente(id=uuid.uuid4(), empresa_id=empresa.id, cliente_id=cliente.id, nombre="Paciente CRM")
    db_session.add_all([empresa, sucursal, cliente, paciente])
    await db_session.flush()

    service = CRMService(db_session)
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    cita = await service.crear_cita(
        empresa_id=empresa.id,
        payload=CitaOpticaCreate(
            sucursal_id=sucursal.id,
            cliente_id=cliente.id,
            paciente_id=paciente.id,
            folio="CITA-1",
            fecha_inicio=inicio,
            fecha_fin=inicio + timedelta(minutes=30),
            motivo="Examen visual anual",
        ),
    )
    cita = await service.cambiar_estado_cita(empresa_id=empresa.id, cita_id=cita.id, estado="CONFIRMADA")
    recordatorio = await service.crear_recordatorio(
        empresa_id=empresa.id,
        payload=RecordatorioClienteCreate(
            cliente_id=cliente.id,
            paciente_id=paciente.id,
            cita_id=cita.id,
            tipo="CITA",
            canal="EMAIL",
            programado_para=inicio - timedelta(hours=24),
            mensaje="Te recordamos tu cita óptica",
        ),
    )

    assert cita.estado == "CONFIRMADA"
    assert recordatorio.estado == "PENDIENTE"
    assert len(await service.listar_citas(empresa_id=empresa.id)) == 1
    assert len(await service.listar_recordatorios_pendientes(empresa_id=empresa.id)) == 1


@pytest.mark.asyncio
async def test_crm_rechaza_paciente_de_otro_cliente(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="CRM Reject SA", rfc="CRR260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="CRR", nombre="CRM Reject")
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente A", email="a.crm@example.com")
    otro_cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente B", email="b.crm@example.com")
    paciente = Paciente(id=uuid.uuid4(), empresa_id=empresa.id, cliente_id=otro_cliente.id, nombre="Paciente B")
    db_session.add_all([empresa, sucursal, cliente, otro_cliente, paciente])
    await db_session.flush()

    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(ValueError, match="Paciente inexistente para el cliente"):
        await CRMService(db_session).crear_cita(
            empresa_id=empresa.id,
            payload=CitaOpticaCreate(
                sucursal_id=sucursal.id,
                cliente_id=cliente.id,
                paciente_id=paciente.id,
                folio="CITA-REJECT",
                fecha_inicio=inicio,
                fecha_fin=inicio + timedelta(minutes=30),
            ),
        )
