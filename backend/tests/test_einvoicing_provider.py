from decimal import Decimal
from uuid import uuid4

import httpx
import pytest

from app.services.einvoicing_provider import (
    EInvoiceLine,
    EInvoicePayload,
    EInvoicingProviderError,
    HttpEInvoicingProvider,
    MockEInvoicingProvider,
)


def _payload() -> EInvoicePayload:
    return EInvoicePayload(
        empresa_id=uuid4(),
        venta_id=uuid4(),
        folio="F-100",
        moneda="MXN",
        subtotal=Decimal("100.00"),
        impuestos=Decimal("16.00"),
        total=Decimal("116.00"),
        lineas=[
            EInvoiceLine(
                producto_id=uuid4(),
                descripcion="Lente oftálmico",
                cantidad=Decimal("1"),
                precio_unitario=Decimal("100.00"),
                descuento=Decimal("0.00"),
                importe=Decimal("100.00"),
            )
        ],
    )


@pytest.mark.asyncio
async def test_mock_einvoicing_provider_is_deterministic():
    provider = MockEInvoicingProvider()
    payload = _payload()

    first = await provider.issue_invoice(payload)
    second = await provider.issue_invoice(payload)

    assert first == second
    assert first.xml_url.endswith(".xml")
    assert first.pdf_url.endswith(".pdf")


@pytest.mark.asyncio
async def test_http_einvoicing_provider_issues_invoice_with_normalized_payload():
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        body = request.read().decode()
        assert '"folio":"F-100"' in body
        assert '"subtotal":"100.00"' in body
        assert request.headers["authorization"] == "Bearer secret-token"
        return httpx.Response(
            201,
            json={
                "uuid_fiscal": "cfdi-uuid",
                "xml_url": "https://pac.example/cfdi-uuid.xml",
                "pdf_url": "https://pac.example/cfdi-uuid.pdf",
            },
        )

    provider = HttpEInvoicingProvider(
        "https://pac.example",
        "secret-token",
        transport=httpx.MockTransport(handler),
    )

    result = await provider.issue_invoice(_payload())

    assert requests[0].url == "https://pac.example/invoices"
    assert result.uuid_fiscal == "cfdi-uuid"
    assert result.xml_url.endswith(".xml")
    assert result.pdf_url.endswith(".pdf")


@pytest.mark.asyncio
async def test_http_einvoicing_provider_cancels_invoice():
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.url == "https://pac.example/invoices/cfdi-uuid/cancel"
        assert '"motivo":"02"' in request.read().decode()
        return httpx.Response(200, json={"cancelled": True})

    provider = HttpEInvoicingProvider(
        "https://pac.example",
        "secret-token",
        transport=httpx.MockTransport(handler),
    )

    await provider.cancel_invoice("cfdi-uuid", "02")

    assert len(requests) == 1


def test_http_einvoicing_provider_requires_credentials():
    with pytest.raises(EInvoicingProviderError):
        HttpEInvoicingProvider("", "secret-token")
    with pytest.raises(EInvoicingProviderError):
        HttpEInvoicingProvider("https://pac.example", "")


@pytest.mark.asyncio
async def test_http_einvoicing_provider_rejects_invalid_issue_response():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"uuid_fiscal": "missing-urls"})

    provider = HttpEInvoicingProvider(
        "https://pac.example",
        "secret-token",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(EInvoicingProviderError):
        await provider.issue_invoice(_payload())
