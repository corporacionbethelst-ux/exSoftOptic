from decimal import Decimal
import uuid

import pytest

from app.models.empresa import Empresa
from app.models.inventario import InventarioExistencia
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.schemas.compras import SolicitudCompraGenerarRequest
from app.services.purchase_requisition_service import PurchaseRequisitionService


@pytest.mark.asyncio
async def test_generar_solicitud_compra_desde_stock_minimo(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Requisitions Test SA", rfc="REQ260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="REQ", nombre="Requisitions")
    producto = Producto(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        sku="REQ-001",
        nombre="Lente con bajo stock",
        precio_venta=Decimal("300"),
        costo_estandar=Decimal("120"),
        stock_minimo=Decimal("10"),
        punto_reorden=Decimal("15"),
    )
    existencia = InventarioExistencia(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("4"),
        costo_promedio=Decimal("120"),
        valor_total=Decimal("480"),
    )
    db_session.add_all([empresa, sucursal, producto, existencia])
    await db_session.flush()

    solicitud = await PurchaseRequisitionService(db_session).generar_desde_stock_minimo(
        empresa_id=empresa.id,
        payload=SolicitudCompraGenerarRequest(sucursal_id=sucursal.id, folio="SC-1"),
    )

    assert solicitud.estado == "BORRADOR"
    assert solicitud.origen == "STOCK_MINIMO"
    assert len(solicitud.lineas) == 1
    assert solicitud.lineas[0].cantidad_sugerida == Decimal("11")
    assert solicitud.lineas[0].costo_estimado == Decimal("120")
