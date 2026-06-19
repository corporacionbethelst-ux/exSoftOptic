from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa
from app.models.inventario import InventarioExistencia, KardexMovimiento
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.models.venta import Cliente, Paciente, RecetaOptica, Venta
from app.schemas.laboratorio import ConsumoMaterialCreate, ControlCalidadCreate, OrdenLaboratorioFromVentaCreate
from app.services.inventory_service import InventoryService
from app.services.lab_service import ETAPAS_ESTANDAR, LabService


async def _base_laboratorio(db_session: AsyncSession, estado_venta="CONFIRMADA"):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Lab Test SA", rfc="LAB260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="LAB", nombre="Laboratorio")
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente Lab", email="lab@example.com")
    paciente = Paciente(id=uuid.uuid4(), empresa_id=empresa.id, cliente_id=cliente.id, nombre="Paciente Lab")
    receta = RecetaOptica(id=uuid.uuid4(), empresa_id=empresa.id, paciente_id=paciente.id, fecha=date(2026, 6, 19))
    venta = Venta(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        cliente_id=cliente.id,
        paciente_id=paciente.id,
        receta_id=receta.id,
        folio="V-LAB-1",
        estado=estado_venta,
        subtotal=Decimal("1000"),
        impuestos=Decimal("0"),
        total=Decimal("1000"),
        costo_total=Decimal("600"),
    )
    material = Producto(id=uuid.uuid4(), empresa_id=empresa.id, sku="CRUDO-LAB-001", nombre="Lente crudo", precio_venta=Decimal("100"))
    db_session.add_all([empresa, sucursal, cliente, paciente, receta, venta, material])
    await db_session.flush()
    return empresa, sucursal, venta, material


@pytest.mark.asyncio
async def test_crear_orden_laboratorio_desde_venta_confirmada(db_session: AsyncSession):
    empresa, _, venta, _ = await _base_laboratorio(db_session)

    orden = await LabService(db_session).crear_orden_desde_venta(
        empresa_id=empresa.id,
        venta_id=venta.id,
        payload=OrdenLaboratorioFromVentaCreate(folio="LAB-100", prioridad="ALTA"),
    )

    assert orden.estado == "PENDIENTE"
    assert orden.venta_id == venta.id
    assert len(orden.etapas) == len(ETAPAS_ESTANDAR)
    assert {etapa.etapa for etapa in orden.etapas} == set(ETAPAS_ESTANDAR)


@pytest.mark.asyncio
async def test_no_crea_orden_laboratorio_desde_venta_no_confirmada(db_session: AsyncSession):
    empresa, _, venta, _ = await _base_laboratorio(db_session, estado_venta="BORRADOR")

    with pytest.raises(ValueError, match="CONFIRMADA"):
        await LabService(db_session).crear_orden_desde_venta(
            empresa_id=empresa.id,
            venta_id=venta.id,
            payload=OrdenLaboratorioFromVentaCreate(folio="LAB-101"),
        )


@pytest.mark.asyncio
async def test_consumo_material_laboratorio_descuenta_inventario(db_session: AsyncSession):
    empresa, sucursal, venta, material = await _base_laboratorio(db_session)
    await InventoryService(db_session).entrada(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=material.id,
        cantidad=Decimal("5"),
        costo_unitario=Decimal("40"),
        origen="COMPRA",
    )
    service = LabService(db_session)
    orden = await service.crear_orden_desde_venta(empresa_id=empresa.id, venta_id=venta.id, payload=OrdenLaboratorioFromVentaCreate(folio="LAB-102"))
    orden = await service.iniciar_orden(empresa_id=empresa.id, orden_id=orden.id)

    consumo = await service.registrar_consumo_material(
        empresa_id=empresa.id,
        orden_id=orden.id,
        payload=ConsumoMaterialCreate(producto_id=material.id, cantidad=Decimal("2")),
    )

    assert consumo.costo_total == Decimal("80")
    existencia = await db_session.scalar(select(InventarioExistencia))
    assert existencia.cantidad == Decimal("3")
    salida = await db_session.scalar(select(KardexMovimiento).where(KardexMovimiento.tipo_movimiento == "SALIDA"))
    assert salida.costo_total == Decimal("-80")


@pytest.mark.asyncio
async def test_control_calidad_aprobado_y_entrega(db_session: AsyncSession):
    empresa, _, venta, _ = await _base_laboratorio(db_session)
    service = LabService(db_session)
    orden = await service.crear_orden_desde_venta(empresa_id=empresa.id, venta_id=venta.id, payload=OrdenLaboratorioFromVentaCreate(folio="LAB-103"))
    orden = await service.iniciar_orden(empresa_id=empresa.id, orden_id=orden.id)

    for _ in ETAPAS_ESTANDAR:
        etapa_en_proceso = next(etapa for etapa in orden.etapas if etapa.estado == "EN_PROCESO")
        orden = await service.completar_etapa(empresa_id=empresa.id, orden_id=orden.id, etapa_id=etapa_en_proceso.id)

    assert orden.estado == "CONTROL_CALIDAD"
    orden = await service.registrar_control_calidad(
        empresa_id=empresa.id,
        orden_id=orden.id,
        payload=ControlCalidadCreate(resultado="APROBADO", observaciones="OK"),
    )
    assert orden.estado == "LISTA_ENTREGA"

    orden = await service.entregar_orden(empresa_id=empresa.id, orden_id=orden.id)
    assert orden.estado == "ENTREGADA"
    assert orden.fecha_entrega is not None
