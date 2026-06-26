import uuid

import pytest

from app.api.deps import get_current_user
from app.main import app
from app.models.empresa import Empresa
from app.models.usuario import Rol, Usuario


@pytest.mark.asyncio
async def test_e2e_health_product_and_audit_flow(client, db_session):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="E2E Smoke SA de CV",
        rfc="E2E260626AA1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    rol = Rol(
        id=uuid.uuid4(),
        nombre="E2E_ADMIN",
        descripcion="Rol de pruebas end-to-end",
        permisos=["*"],
        empresa_id=empresa.id,
    )
    usuario = Usuario(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        username="e2e.admin",
        email="e2e.admin@example.com",
        password_hash="not-used-in-e2e",
        nombre_completo="Administrador E2E",
        rol_id=rol.id,
        esta_activo=True,
    )
    usuario.rol = rol
    db_session.add_all([empresa, rol, usuario])
    await db_session.flush()

    async def override_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_current_user

    health = await client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    producto_payload = {
        "sku": "E2E-ARMAZON-001",
        "nombre": "Armazón E2E",
        "descripcion": "Producto creado desde smoke test end-to-end",
        "tipo_producto": "ARMAZON",
        "unidad_medida": "PIEZA",
        "costo_estandar": "500.00",
        "precio_venta": "1200.00",
        "stock_minimo": "2",
    }
    created = await client.post("/api/v1/productos/", json=producto_payload)
    assert created.status_code == 201
    created_body = created.json()
    assert created_body["sku"] == producto_payload["sku"]
    assert created_body["empresa_id"] == str(empresa.id)

    listed = await client.get("/api/v1/productos/")
    assert listed.status_code == 200
    listed_body = listed.json()
    assert listed_body["total"] == 1
    assert listed_body["items"][0]["sku"] == producto_payload["sku"]

    audit_chain = await client.get("/api/v1/auditoria/verificar-cadena")
    assert audit_chain.status_code == 200
    audit_body = audit_chain.json()
    assert audit_body["valid"] is True
    assert audit_body["total_events"] >= 1
