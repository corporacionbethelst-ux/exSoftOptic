from __future__ import annotations

import sys

from scripts import seed_demo_data


def test_main_reports_database_connection_failure(monkeypatch, capsys):
    async def unavailable(**_kwargs):
        raise OSError("Connect call failed ('127.0.0.1', 5432)")

    monkeypatch.setattr(seed_demo_data, "seed_demo_data", unavailable)
    monkeypatch.setattr(sys, "argv", ["seed_demo_data.py"])

    assert seed_demo_data.main() == 2

    error = capsys.readouterr().err
    assert "No fue posible conectar con PostgreSQL" in error
    assert "make db-up" in error
    assert "make migrate-up" in error
    assert "127.0.0.1" in error
