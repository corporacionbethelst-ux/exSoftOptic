from datetime import date
from decimal import Decimal
import uuid

import pytest

from app.models.empresa import Empresa
from app.models.venta import Cliente, Paciente, RecetaOptica
from app.services.privacy_service import PrivacyService


@pytest.mark.asyncio
async def test_subject_export_and_anonymization_are_tenant_scoped(db_session):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Privacy Test SA",
        rfc="PRI260808AA1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    cliente = Cliente(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        nombre="Persona Identificable",
        email="persona@example.com",
        telefono="5551234567",
        rfc="PEID900101AA1",
    )
    paciente = Paciente(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        cliente_id=cliente.id,
        nombre="Paciente Identificable",
        fecha_nacimiento=date(1990, 1, 1),
        email="paciente@example.com",
    )
    receta = RecetaOptica(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        paciente_id=paciente.id,
        fecha=date(2026, 8, 8),
        od_esfera=Decimal("-1.25"),
        observaciones="Dato clínico libre",
    )
    db_session.add_all([empresa, cliente, paciente, receta])
    await db_session.flush()

    service = PrivacyService(db_session)
    exported = await service.export_subject(empresa_id=empresa.id, cliente_id=cliente.id)
    assert exported["cliente"]["email"] == "persona@example.com"
    assert exported["pacientes"][0]["fecha_nacimiento"] == "1990-01-01"
    assert exported["recetas"][0]["od_esfera"] == "-1.25"

    result = await service.anonymize_subject(empresa_id=empresa.id, cliente_id=cliente.id)
    assert result["patients_anonymized"] == 1
    assert result["prescriptions_redacted"] == 1
    assert cliente.nombre.startswith("ANONIMIZADO-")
    assert cliente.email is None and cliente.rfc is None and cliente.deleted_at is not None
    assert paciente.nombre.startswith("ANONIMIZADO-")
    assert paciente.fecha_nacimiento is None and paciente.email is None
    assert receta.observaciones is None


@pytest.mark.asyncio
async def test_subject_export_rejects_cross_tenant_access(db_session):
    empresa = Empresa(
        id=uuid.uuid4(), razon_social="Privacy Owner SA", rfc="PRO260808AA1", regimen_fiscal="601", codigo_postal="06600"
    )
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Owner")
    db_session.add_all([empresa, cliente])
    await db_session.flush()

    with pytest.raises(ValueError, match="Cliente inexistente"):
        await PrivacyService(db_session).export_subject(
            empresa_id=uuid.uuid4(), cliente_id=cliente.id
        )
