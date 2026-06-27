from pathlib import Path

from scripts.audit_query_pagination import find_unpaginated_gets


def test_pagination_audit_reports_list_endpoint_without_limit(tmp_path: Path):
    endpoint = tmp_path / "items.py"
    endpoint.write_text(
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.get('/items', response_model=list[str])\n"
        "async def list_items():\n"
        "    return []\n"
    )

    findings = find_unpaginated_gets(tmp_path)

    assert len(findings) == 1
    assert findings[0].function == "list_items"


def test_pagination_audit_accepts_list_endpoint_with_limit(tmp_path: Path):
    endpoint = tmp_path / "items.py"
    endpoint.write_text(
        "from fastapi import APIRouter, Query\n"
        "router = APIRouter()\n"
        "@router.get('/items', response_model=list[str])\n"
        "async def list_items(limit: int = Query(100)):\n"
        "    return []\n"
    )

    assert find_unpaginated_gets(tmp_path) == []
