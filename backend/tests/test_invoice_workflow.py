from decimal import Decimal
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.models.venta import Cliente, Venta, VentaLinea
from app.schemas.facturacion import FacturaCancelarRequest, FacturaEmitirRequest
from app.services.invoice_service import InvoiceService


async def _base_factura(db_session: AsyncSession, estado_venta="CONFIRMADA"):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Factura Test SA", rfc="FAC260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="F1", nombre="Facturación")
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente Factura")
    producto = Producto(id=uuid.uuid4(), empresa_id=empresa.id, sku="PROD-FAC-001", nombre="Producto factura", precio_venta=Decimal("1000"))
    venta = Venta(
        id=uuid.uuid4(), empresa_id=empresa.id, sucursal_id=sucursal.id, cliente_id=cliente.id,
        folio="V-FAC-1", estado=estado_venta, subtotal=Decimal("1000"), impuestos=Decimal("160"),
        total=Decimal("1160"), costo_total=Decimal("500"),
    )
    linea = VentaLinea(
        venta_id=venta.id, producto_id=producto.id, descripcion="Producto factura", cantidad=Decimal("1"),
        precio_unitario=Decimal("1000"), descuento=Decimal("0"), importe=Decimal("1000"), costo_total=Decimal("500"),
    )
    db_session.add_all([empresa, sucursal, cliente, producto, venta, linea])
    await db_session.flush()
    return empresa, venta


@pytest.mark.asyncio
async def test_emitir_factura_desde_venta_confirmada(db_session: AsyncSession):
    empresa, venta = await _base_factura(db_session)

    factura = await InvoiceService(db_session).emitir_desde_venta(
        empresa_id=empresa.id,
        payload=FacturaEmitirRequest(venta_id=venta.id, folio="FAC-100"),
    )

    assert factura.estado == "TIMBRADA"
    assert factura.uuid_fiscal is not None
    assert factura.total == Decimal("1160")
    assert len(factura.lineas) == 1
    assert len(factura.eventos) == 1


@pytest.mark.asyncio
async def test_no_emite_factura_desde_venta_no_confirmada(db_session: AsyncSession):
    empresa, venta = await _base_factura(db_session, estado_venta="BORRADOR")

    with pytest.raises(ValueError, match="CONFIRMADA"):
        await InvoiceService(db_session).emitir_desde_venta(
            empresa_id=empresa.id,
            payload=FacturaEmitirRequest(venta_id=venta.id, folio="FAC-101"),
        )


@pytest.mark.asyncio
async def test_cancelar_factura_timbrada(db_session: AsyncSession):
    empresa, venta = await _base_factura(db_session)
    service = InvoiceService(db_session)
    factura = await service.emitir_desde_venta(
        empresa_id=empresa.id,
        payload=FacturaEmitirRequest(venta_id=venta.id, folio="FAC-102"),
    )

    factura = await service.cancelar_factura(
        empresa_id=empresa.id,
        factura_id=factura.id,
        payload=FacturaCancelarRequest(motivo="Cancelación de prueba"),
    )

    assert factura.estado == "CANCELADA"
    assert len(factura.eventos) == 2
