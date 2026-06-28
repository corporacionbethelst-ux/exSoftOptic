from pathlib import Path

from scripts.audit_api_contract import ApiContractFinding, audit_api_contract, parse_endpoint_routes, parse_router_includes


def test_api_contract_audit_passes_current_router():
    assert audit_api_contract() == []


def test_api_contract_audit_detects_unregistered_endpoint(tmp_path: Path):
    endpoints = tmp_path / "endpoints"
    endpoints.mkdir()
    (endpoints / "ventas.py").write_text('from fastapi import APIRouter\nrouter = APIRouter()\n@router.get("/")\nasync def listar():\n    return []\n')
    router = tmp_path / "router.py"
    router.write_text('from fastapi import APIRouter\napi_router = APIRouter()\n')

    findings = audit_api_contract(endpoints_dir=endpoints, router_file=router)

    assert ApiContractFinding("endpoint-not-registered", "Endpoint module `ventas` is not included in api_router.") in findings


def test_api_contract_audit_detects_duplicate_routes(tmp_path: Path):
    endpoints = tmp_path / "endpoints"
    endpoints.mkdir()
    route_source = 'from fastapi import APIRouter\nrouter = APIRouter()\n@router.get("/")\nasync def listar():\n    return []\n'
    (endpoints / "ventas.py").write_text(route_source)
    (endpoints / "ventas_alias.py").write_text(route_source)
    router = tmp_path / "router.py"
    router.write_text(
        'from fastapi import APIRouter\n'
        'from app.api.v1.endpoints import ventas, ventas_alias\n'
        'api_router = APIRouter()\n'
        'api_router.include_router(ventas.router, prefix="/ventas", tags=["Ventas"])\n'
        'api_router.include_router(ventas_alias.router, prefix="/ventas", tags=["Ventas Alias"])\n'
    )

    findings = audit_api_contract(endpoints_dir=endpoints, router_file=router)

    assert any(finding.code == "duplicate-route" for finding in findings)


def test_api_contract_parsers_extract_routes_and_includes(tmp_path: Path):
    endpoint = tmp_path / "productos.py"
    endpoint.write_text('from fastapi import APIRouter\nrouter = APIRouter()\n@router.post("/crear")\nasync def crear():\n    return {}\n')
    router = tmp_path / "router.py"
    router.write_text('api_router.include_router(productos.router, prefix="/productos", tags=["Productos"])\n')

    assert parse_endpoint_routes(endpoint)[0].path == "/crear"
    assert parse_router_includes(router)[0].prefix == "/productos"
