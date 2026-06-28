#!/usr/bin/env python3
"""Statically audit API router registration and endpoint route declarations."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS_DIR = BACKEND_ROOT / "app" / "api" / "v1" / "endpoints"
ROUTER_FILE = BACKEND_ROOT / "app" / "api" / "v1" / "router.py"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
STALE_MARKERS = ("TODO", "Paso 4", "se agregarán cuando")


@dataclass(frozen=True)
class RouteDeclaration:
    module: str
    method: str
    path: str
    line: int


@dataclass(frozen=True)
class RouterInclude:
    module: str
    prefix: str
    tags: tuple[str, ...]
    line: int


@dataclass(frozen=True)
class ApiContractFinding:
    code: str
    detail: str


def parse_endpoint_routes(path: Path) -> list[RouteDeclaration]:
    module = path.stem
    tree = ast.parse(path.read_text(), filename=str(path))
    routes: list[RouteDeclaration] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute) or func.attr not in HTTP_METHODS:
                continue
            if not isinstance(func.value, ast.Name) or func.value.id != "router":
                continue
            route_path = _first_string_arg(decorator) or "<unknown>"
            routes.append(RouteDeclaration(module=module, method=func.attr.upper(), path=route_path, line=decorator.lineno))
    return routes


def parse_router_includes(router_file: Path = ROUTER_FILE) -> list[RouterInclude]:
    tree = ast.parse(router_file.read_text(), filename=str(router_file))
    includes: list[RouterInclude] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "include_router":
            continue
        if not node.args or not isinstance(node.args[0], ast.Attribute):
            continue
        router_arg = node.args[0]
        if router_arg.attr != "router" or not isinstance(router_arg.value, ast.Name):
            continue
        prefix = _keyword_string(node, "prefix") or ""
        tags = tuple(_keyword_string_list(node, "tags"))
        includes.append(RouterInclude(module=router_arg.value.id, prefix=prefix, tags=tags, line=node.lineno))
    return includes


def _first_string_arg(node: ast.Call) -> str | None:
    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        return node.args[0].value
    return None


def _keyword_string(node: ast.Call, name: str) -> str | None:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            return keyword.value.value
    return None


def _keyword_string_list(node: ast.Call, name: str) -> list[str]:
    for keyword in node.keywords:
        if keyword.arg != name or not isinstance(keyword.value, ast.List):
            continue
        return [item.value for item in keyword.value.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
    return []


def _full_path(prefix: str, route_path: str) -> str:
    if route_path == "/":
        return prefix or "/"
    return f"{prefix.rstrip('/')}/{route_path.lstrip('/')}"


def _has_stale_marker(path: Path) -> bool:
    text = path.read_text()
    return any(marker in text for marker in STALE_MARKERS)


def audit_api_contract(endpoints_dir: Path = ENDPOINTS_DIR, router_file: Path = ROUTER_FILE) -> list[ApiContractFinding]:
    findings: list[ApiContractFinding] = []
    endpoint_files = sorted(path for path in endpoints_dir.glob("*.py") if path.name != "__init__.py")
    endpoint_modules = {path.stem for path in endpoint_files}
    includes = parse_router_includes(router_file)
    included_modules = {include.module for include in includes}

    for path in [router_file, *endpoint_files]:
        if _has_stale_marker(path):
            findings.append(ApiContractFinding("stale-api-marker", f"Remove stale TODO/planning marker from `{path.relative_to(BACKEND_ROOT)}`."))

    for path in endpoint_files:
        routes = parse_endpoint_routes(path)
        if not routes:
            findings.append(ApiContractFinding("endpoint-without-routes", f"Endpoint module `{path.name}` declares no routes."))

    for module in sorted(endpoint_modules - included_modules):
        findings.append(ApiContractFinding("endpoint-not-registered", f"Endpoint module `{module}` is not included in api_router."))

    for module in sorted(included_modules - endpoint_modules):
        findings.append(ApiContractFinding("router-missing-module", f"api_router includes `{module}` but no endpoint module exists."))

    for include in includes:
        if not include.prefix.startswith("/"):
            findings.append(ApiContractFinding("invalid-prefix", f"Router `{include.module}` prefix must start with `/`."))
        if not include.tags:
            findings.append(ApiContractFinding("missing-tags", f"Router `{include.module}` must declare non-empty tags."))

    route_index: dict[tuple[str, str], RouteDeclaration] = {}
    includes_by_module = {include.module: include for include in includes}
    for path in endpoint_files:
        include = includes_by_module.get(path.stem)
        if include is None:
            continue
        for route in parse_endpoint_routes(path):
            key = (route.method, _full_path(include.prefix, route.path))
            previous = route_index.get(key)
            if previous:
                findings.append(ApiContractFinding("duplicate-route", f"{route.module}:{route.line} duplicates {previous.module}:{previous.line} for {key[0]} {key[1]}."))
            else:
                route_index[key] = route

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoints-dir", type=Path, default=ENDPOINTS_DIR)
    parser.add_argument("--router-file", type=Path, default=ROUTER_FILE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = audit_api_contract(endpoints_dir=args.endpoints_dir, router_file=args.router_file)
    if findings:
        for finding in findings:
            print(f"❌ {finding.code}: {finding.detail}")
        return 1
    print("✅ API contract audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
