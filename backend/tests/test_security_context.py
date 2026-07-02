import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.deps import require_empresa_scope, require_sucursal_scope


def test_require_empresa_scope_blocks_cross_tenant_access():
    current_user = SimpleNamespace(empresa_id=uuid.uuid4(), sucursal_id=None)

    with pytest.raises(HTTPException) as exc:
        require_empresa_scope(uuid.uuid4(), current_user)

    assert exc.value.status_code == 403


def test_require_sucursal_scope_allows_only_assigned_branch():
    allowed_sucursal = uuid.uuid4()
    current_user = SimpleNamespace(empresa_id=uuid.uuid4(), sucursal_id=allowed_sucursal)

    require_sucursal_scope(allowed_sucursal, current_user)
    with pytest.raises(HTTPException) as exc:
        require_sucursal_scope(uuid.uuid4(), current_user)

    assert exc.value.status_code == 403
