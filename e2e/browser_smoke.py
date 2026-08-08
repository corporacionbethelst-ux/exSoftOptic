#!/usr/bin/env python3
"""Browser smoke tests for authentication, navigation and token refresh."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import Page, Route, expect, sync_playwright


USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "username": "admin",
    "email": "admin@example.com",
    "nombre_completo": "Administrador E2E",
    "rol_id": "00000000-0000-0000-0000-000000000002",
    "empresa_id": "00000000-0000-0000-0000-000000000003",
    "sucursal_id": None,
    "esta_activo": True,
    "email_verificado": True,
    "ultimo_acceso": None,
    "created_at": "2026-01-01T00:00:00Z",
}


def json_response(route: Route, payload: object, status: int = 200) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=json.dumps(payload),
    )


def install_api_mock(page: Page) -> dict[str, int]:
    calls: dict[str, int] = {}

    def handler(route: Route) -> None:
        request = route.request
        path = request.url.split("?", 1)[0]
        normalized_path = path.rstrip("/")
        calls[path] = calls.get(path, 0) + 1
        if path.endswith("/api/v1/auth/login"):
            body = request.post_data_json
            if body.get("username") == "invalid":
                json_response(
                    route,
                    {"error": {"code": "INVALID_CREDENTIALS", "message": "Credenciales inválidas"}},
                    401,
                )
            else:
                json_response(
                    route,
                    {
                        "access_token": "access-e2e",
                        "refresh_token": "refresh-e2e",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": USER,
                    },
                )
            return
        if path.endswith("/api/v1/auth/refresh"):
            json_response(
                route,
                {
                    "access_token": "access-refreshed-e2e",
                    "refresh_token": "refresh-rotated-e2e",
                    "token_type": "bearer",
                    "expires_in": 1800,
                },
            )
            return
        if path.endswith("/api/v1/auth/me"):
            authorization = request.headers.get("authorization", "")
            if authorization == "Bearer access-expired-e2e":
                json_response(route, {"detail": "expired"}, 401)
            else:
                json_response(route, USER)
            return
        if path.endswith("/api/v1/auth/logout"):
            json_response(route, {"message": "Sesión cerrada"})
            return
        if normalized_path.endswith("/api/v1/usuarios"):
            json_response(route, {"total": 1, "page": 1, "per_page": 20, "users": [USER]})
            return
        if normalized_path.endswith("/api/v1/productos"):
            json_response(route, {"items": [], "productos": [], "total": 0})
            return
        if "/api/" in path:
            json_response(route, [])
            return
        route.continue_()

    page.route("**/*", handler)
    return calls


def test_login_validation_and_navigation(page: Page, base_url: str) -> None:
    install_api_mock(page)
    page.goto(base_url)
    expect(page.get_by_role("heading", name="Panel administrativo para ópticas")).to_be_visible()

    page.get_by_label("Usuario").fill("invalid")
    page.get_by_label("Contraseña").fill("wrong")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_text("Credenciales inválidas")).to_be_visible()

    page.get_by_label("Usuario").fill("admin")
    page.get_by_label("Contraseña").fill("Admin123!")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Dashboard operativo")).to_be_visible()
    expect(page.get_by_text("Administrador E2E")).to_be_visible()

    page.get_by_role("button", name="Usuarios").click()
    expect(page.get_by_role("heading", name="Usuarios y roles")).to_be_visible()
    page.get_by_role("button", name="Salir").click()
    expect(page.get_by_role("heading", name="Panel administrativo para ópticas")).to_be_visible()


def test_expired_access_token_is_refreshed(page: Page, base_url: str) -> None:
    calls = install_api_mock(page)
    page.add_init_script(
        """
        localStorage.setItem('exsoftoptic.tokens', JSON.stringify({
          access_token: 'access-expired-e2e',
          refresh_token: 'refresh-e2e',
          token_type: 'bearer',
          expires_in: 0,
          user: %s
        }));
        """ % json.dumps(USER)
    )
    page.goto(base_url)
    expect(page.get_by_role("heading", name="Dashboard operativo")).to_be_visible()
    refresh_path = f"{base_url.rstrip('/')}/api/v1/auth/refresh"
    assert calls.get(refresh_path) == 1
    stored = page.evaluate("JSON.parse(localStorage.getItem('exsoftoptic.tokens'))")
    assert stored["access_token"] == "access-refreshed-e2e"
    assert stored["refresh_token"] == "refresh-rotated-e2e"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:4173")
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/e2e"))
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        try:
            test_login_validation_and_navigation(context.new_page(), args.base_url)
            test_expired_access_token_is_refreshed(context.new_page(), args.base_url)
        except Exception:
            context.pages[-1].screenshot(path=args.artifacts / "failure.png", full_page=True)
            raise
        finally:
            context.tracing.stop(path=args.artifacts / "trace.zip")
            browser.close()
    print("✅ browser smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
