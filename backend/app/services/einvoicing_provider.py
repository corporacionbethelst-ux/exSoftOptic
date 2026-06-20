from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_URL


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


def get_einvoicing_provider(name: str) -> EInvoicingProvider:
    if name.upper() == "MOCK":
        return MockEInvoicingProvider()
    raise ValueError(f"Proveedor de facturación no soportado: {name}")
