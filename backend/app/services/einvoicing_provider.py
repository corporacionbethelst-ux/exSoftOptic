from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, NAMESPACE_URL, uuid5

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class EInvoiceLine:
    producto_id: UUID
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    descuento: Decimal
    importe: Decimal


@dataclass(frozen=True)
class EInvoicePayload:
    empresa_id: UUID
    venta_id: UUID
    folio: str
    moneda: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal
    lineas: list[EInvoiceLine]


@dataclass(frozen=True)
class EInvoiceResult:
    uuid_fiscal: str
    xml_url: str
    pdf_url: str


class EInvoicingProviderError(RuntimeError):
    """Raised when an external e-invoicing provider cannot complete an operation."""


class EInvoicingProvider:
    async def issue_invoice(self, payload: EInvoicePayload) -> EInvoiceResult:
        raise NotImplementedError

    async def cancel_invoice(self, uuid_fiscal: str, motivo: str) -> None:
        raise NotImplementedError


class MockEInvoicingProvider(EInvoicingProvider):
    async def issue_invoice(self, payload: EInvoicePayload) -> EInvoiceResult:
        uuid_fiscal = str(uuid5(NAMESPACE_URL, f"{payload.empresa_id}:{payload.venta_id}:{payload.folio}"))
        return EInvoiceResult(
            uuid_fiscal=uuid_fiscal,
            xml_url=f"mock://cfdi/{uuid_fiscal}.xml",
            pdf_url=f"mock://cfdi/{uuid_fiscal}.pdf",
        )

    async def cancel_invoice(self, uuid_fiscal: str, motivo: str) -> None:
        if not motivo:
            raise ValueError("Se requiere motivo de cancelación")


class HttpEInvoicingProvider(EInvoicingProvider):
    """HTTP adapter for production CFDI/e-invoicing providers.

    The adapter keeps the internal service layer independent from a concrete
    PAC/CFDI vendor. Providers can expose the normalized `/invoices` and
    `/invoices/{uuid}/cancel` contract through an API gateway or thin adapter.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not base_url:
            raise EInvoicingProviderError("CFDI_API_URL es obligatorio para el proveedor HTTP")
        if not api_key:
            raise EInvoicingProviderError("CFDI_API_KEY es obligatorio para el proveedor HTTP")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def issue_invoice(self, payload: EInvoicePayload) -> EInvoiceResult:
        response = await self._post("/invoices", self._payload_to_json(payload))
        return self._result_from_response(response)

    async def cancel_invoice(self, uuid_fiscal: str, motivo: str) -> None:
        if not motivo:
            raise ValueError("Se requiere motivo de cancelación")
        await self._post(f"/invoices/{uuid_fiscal}/cancel", {"motivo": motivo})

    async def _post(self, path: str, json_payload: dict) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._headers(),
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.post(path, json=json_payload)
                response.raise_for_status()
                if not response.content:
                    return {}
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise EInvoicingProviderError(
                f"Proveedor CFDI respondió {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:
            raise EInvoicingProviderError(f"Error al comunicarse con proveedor CFDI: {exc}") from exc

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _payload_to_json(self, payload: EInvoicePayload) -> dict:
        return {
            "empresa_id": str(payload.empresa_id),
            "venta_id": str(payload.venta_id),
            "folio": payload.folio,
            "moneda": payload.moneda,
            "subtotal": str(payload.subtotal),
            "impuestos": str(payload.impuestos),
            "total": str(payload.total),
            "lineas": [
                {
                    "producto_id": str(linea.producto_id),
                    "descripcion": linea.descripcion,
                    "cantidad": str(linea.cantidad),
                    "precio_unitario": str(linea.precio_unitario),
                    "descuento": str(linea.descuento),
                    "importe": str(linea.importe),
                }
                for linea in payload.lineas
            ],
        }

    def _result_from_response(self, response: dict) -> EInvoiceResult:
        uuid_fiscal = response.get("uuid_fiscal")
        xml_url = response.get("xml_url")
        pdf_url = response.get("pdf_url")
        if not uuid_fiscal or not xml_url or not pdf_url:
            raise EInvoicingProviderError(
                "Respuesta CFDI inválida: se requieren uuid_fiscal, xml_url y pdf_url"
            )
        return EInvoiceResult(uuid_fiscal=uuid_fiscal, xml_url=xml_url, pdf_url=pdf_url)


def get_einvoicing_provider(name: str) -> EInvoicingProvider:
    provider_name = (name or settings.CFDI_PROVIDER).upper()
    if provider_name == "MOCK":
        return MockEInvoicingProvider()
    if provider_name in {"HTTP", "API"}:
        return HttpEInvoicingProvider(
            settings.CFDI_API_URL,
            settings.CFDI_API_KEY,
            settings.CFDI_TIMEOUT_SECONDS,
        )
    raise ValueError(f"Proveedor de facturación no soportado: {name}")
