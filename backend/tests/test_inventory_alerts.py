from decimal import Decimal
import uuid

import pytest

from app.models.empresa import Empresa
from app.models.inventario import InventarioExistencia
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.services.inventory_alert_service import InventoryAlertService


@pytest.mark.asyncio
async def test_alertas_stock_minimo_detecta_stock_bajo_y_critico(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Alertas Test SA", rfc="ALT260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="ALT", nombre="Alertas")
    producto = Producto(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        sku="ALERTA-001",
        nombre="Lente contacto alerta",
        precio_venta=Decimal("250"),
        stock_minimo=Decimal("10"),
        punto_reorden=Decimal("12"),
    )
    existencia = InventarioExistencia(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("4"),
        costo_promedio=Decimal("100"),
        valor_total=Decimal("400"),
    )
    db_session.add_all([empresa, sucursal, producto, existencia])
    await db_session.flush()

    alertas = await InventoryAlertService(db_session).alertas_stock_minimo(empresa_id=empresa.id, sucursal_id=sucursal.id)

    assert len(alertas) == 1
    assert alertas[0].sku == "ALERTA-001"
    assert alertas[0].severidad == "CRITICA"
    assert alertas[0].cantidad_actual == Decimal("4")
