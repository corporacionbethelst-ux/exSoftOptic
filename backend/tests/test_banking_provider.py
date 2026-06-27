from datetime import date
from decimal import Decimal

import httpx
import pytest

from app.services.banking_provider import (
    BankingProviderError,
    CsvBankStatementProvider,
    HttpBankStatementProvider,
)


@pytest.mark.asyncio
async def test_csv_bank_statement_provider_parses_and_filters_movements():
    provider = CsvBankStatementProvider(
        "fecha,referencia,descripcion,monto,tipo\n"
        "2026-06-01,DEP-1,Depósito,100.50,ABONO\n"
        "2026-06-05,CH-1,Cheque,-20.00,CARGO\n"
    )

    movements = await provider.fetch_statement(
        "123",
        date_from=date(2026, 6, 2),
        date_to=date(2026, 6, 30),
    )

    assert len(movements) == 1
    assert movements[0].referencia == "CH-1"
    assert movements[0].monto == Decimal("-20.00")
    assert movements[0].tipo == "CARGO"


@pytest.mark.asyncio
async def test_http_bank_statement_provider_fetches_normalized_movements():
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.headers["authorization"] == "Bearer bank-token"
        assert request.url.params["date_from"] == "2026-06-01"
        assert request.url.params["date_to"] == "2026-06-30"
        return httpx.Response(
            200,
            json={
                "movements": [
                    {
                        "fecha": "2026-06-15",
                        "referencia": "API-1",
                        "descripcion": "Transferencia",
                        "monto": "250.00",
                        "tipo": "ABONO",
                    }
                ]
            },
        )

    provider = HttpBankStatementProvider(
        "https://bank.example",
        "bank-token",
        transport=httpx.MockTransport(handler),
    )

    movements = await provider.fetch_statement(
        "123",
        date_from=date(2026, 6, 1),
        date_to=date(2026, 6, 30),
    )

    assert requests[0].url.path == "/accounts/123/statement"
    assert movements[0].referencia == "API-1"
    assert movements[0].monto == Decimal("250.00")


def test_banking_providers_validate_required_inputs():
    with pytest.raises(BankingProviderError):
        CsvBankStatementProvider("fecha,referencia,monto\n").parse("fecha,referencia,monto\n")
    with pytest.raises(BankingProviderError):
        HttpBankStatementProvider("", "bank-token")
    with pytest.raises(BankingProviderError):
        HttpBankStatementProvider("https://bank.example", "")
