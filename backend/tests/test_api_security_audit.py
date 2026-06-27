from scripts.audit_api_security import PUBLIC_ENDPOINT_ALLOWLIST, audit_endpoints, route_path


def test_api_security_audit_has_no_unprotected_endpoint_findings():
    assert audit_endpoints() == []


def test_api_security_audit_keeps_public_allowlist_explicit_and_small():
    assert ("auth.py", "/login") in PUBLIC_ENDPOINT_ALLOWLIST
    assert ("observabilidad.py", "/readiness") in PUBLIC_ENDPOINT_ALLOWLIST
    assert len(PUBLIC_ENDPOINT_ALLOWLIST) == 5


def test_api_security_audit_extracts_route_paths():
    assert route_path('@router.post("/ordenes", response_model=dict)') == "/ordenes"
