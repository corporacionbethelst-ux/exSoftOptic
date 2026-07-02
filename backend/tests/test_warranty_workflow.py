from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa
from app.models.laboratorio import OrdenLaboratorio
from app.models.sucursal import Sucursal
from app.models.venta import Cliente, Paciente, RecetaOptica, Venta
from app.schemas.garantias import GarantiaFromOrdenCreate, ReclamacionGarantiaCreate, ResolverReclamacionRequest
from app.services.warranty_service import WarrantyService


async def _base_garantia(db_session: AsyncSession, estado_orden="ENTREGADA"):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Garantia Test SA", rfc="GAR260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="G1", nombre="Garantías")
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente Garantía")
    paciente = Paciente(id=uuid.uuid4(), empresa_id=empresa.id, cliente_id=cliente.id, nombre="Paciente Garantía")
    receta = RecetaOptica(id=uuid.uuid4(), empresa_id=empresa.id, paciente_id=paciente.id, fecha=date(2026, 6, 19))
    venta = Venta(
        id=uuid.uuid4(), empresa_id=empresa.id, sucursal_id=sucursal.id, cliente_id=cliente.id,
        paciente_id=paciente.id, receta_id=receta.id, folio="V-GAR-1", estado="CONFIRMADA",
        subtotal=Decimal("1000"), impuestos=Decimal("0"), total=Decimal("1000"), costo_total=Decimal("600"),
    )
    orden = OrdenLaboratorio(
        id=uuid.uuid4(), empresa_id=empresa.id, sucursal_id=sucursal.id, venta_id=venta.id,
        paciente_id=paciente.id, receta_id=receta.id, folio="LAB-GAR-1", estado=estado_orden,
    )
    db_session.add_all([empresa, sucursal, cliente, paciente, receta, venta, orden])
    await db_session.flush()
    return empresa, orden


@pytest.mark.asyncio
async def test_crear_garantia_desde_orden_laboratorio_entregada(db_session: AsyncSession):
    empresa, orden = await _base_garantia(db_session)

    garantia = await WarrantyService(db_session).crear_desde_orden_laboratorio(
        empresa_id=empresa.id,
        orden_id=orden.id,
        payload=GarantiaFromOrdenCreate(
            folio="GAR-100",
            tipo="LENTE",
            fecha_inicio=date(2026, 6, 19),
            fecha_fin=date(2027, 6, 19),
            descripcion="Garantía de lentes",
        ),
    )

    assert garantia.estado == "ACTIVA"
    assert garantia.orden_laboratorio_id == orden.id
    assert garantia.paciente_id == orden.paciente_id
    assert len(garantia.eventos) == 1


@pytest.mark.asyncio
async def test_no_crea_garantia_desde_orden_no_entregada(db_session: AsyncSession):
    empresa, orden = await _base_garantia(db_session, estado_orden="EN_PROCESO")

    with pytest.raises(ValueError, match="ENTREGADA"):
        await WarrantyService(db_session).crear_desde_orden_laboratorio(
            empresa_id=empresa.id,
            orden_id=orden.id,
            payload=GarantiaFromOrdenCreate(
                folio="GAR-101",
                tipo="LENTE",
                fecha_inicio=date(2026, 6, 19),
                fecha_fin=date(2027, 6, 19),
            ),
        )


@pytest.mark.asyncio
async def test_reclamacion_garantia_cambia_estado_y_registra_eventos(db_session: AsyncSession):
    empresa, orden = await _base_garantia(db_session)
    service = WarrantyService(db_session)
    garantia = await service.crear_desde_orden_laboratorio(
        empresa_id=empresa.id,
        orden_id=orden.id,
        payload=GarantiaFromOrdenCreate(
            folio="GAR-102",
            tipo="TRATAMIENTO",
            fecha_inicio=date(2026, 6, 19),
            fecha_fin=date(2027, 6, 19),
        ),
    )

    reclamacion = await service.abrir_reclamacion(
        empresa_id=empresa.id,
        garantia_id=garantia.id,
        payload=ReclamacionGarantiaCreate(folio="REC-100", motivo="Tratamiento defectuoso"),
    )
    assert reclamacion.estado == "ABIERTA"

    garantia = await service.resolver_reclamacion(
        empresa_id=empresa.id,
        reclamacion_id=reclamacion.id,
        payload=ResolverReclamacionRequest(estado="APROBADA", resolucion="Se autoriza reposición"),
    )
    assert garantia.estado == "EN_RECLAMO"
    assert len(garantia.reclamaciones) == 1
    assert len(garantia.eventos) == 3
