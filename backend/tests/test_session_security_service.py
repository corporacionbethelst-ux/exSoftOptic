from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.services.session_security_service import SessionSecurityService


class FakeDB:
    async def flush(self):
        return None


@pytest.mark.asyncio
async def test_record_failed_login_locks_user_after_threshold(monkeypatch):
    monkeypatch.setattr("app.services.session_security_service.settings.MAX_FAILED_LOGIN_ATTEMPTS", 2)
    monkeypatch.setattr("app.services.session_security_service.settings.ACCOUNT_LOCK_MINUTES", 10)
    user = SimpleNamespace(intentos_fallidos=1, bloqueado_hasta=None)

    await SessionSecurityService(FakeDB()).record_failed_login(usuario=user)

    assert user.intentos_fallidos == 2
    assert user.bloqueado_hasta > datetime.now(timezone.utc) + timedelta(minutes=9)


@pytest.mark.asyncio
async def test_clear_failed_logins_resets_lock_state():
    user = SimpleNamespace(intentos_fallidos=3, bloqueado_hasta=datetime.now(timezone.utc))

    await SessionSecurityService(FakeDB()).clear_failed_logins(usuario=user)

    assert user.intentos_fallidos == 0
    assert user.bloqueado_hasta is None
