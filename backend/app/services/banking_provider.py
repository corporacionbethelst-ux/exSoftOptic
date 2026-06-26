import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class BankStatementMovement:
    fecha: date
    referencia: str
    descripcion: str | None
    monto: Decimal
    tipo: str


class BankingProviderError(RuntimeError):
    """Raised when a bank statement provider cannot return normalized movements."""


class BankStatementProvider:
    async def fetch_statement(self, account_number: str, *, date_from: date, date_to: date) -> list[BankStatementMovement]:
        raise NotImplementedError


class CsvBankStatementProvider(BankStatementProvider):
    """Parse bank movements from a CSV payload with normalized columns."""

    REQUIRED_COLUMNS = {"fecha", "referencia", "monto", "tipo"}

    def __init__(self, csv_content: str) -> None:
        self.csv_content = csv_content

    async def fetch_statement(self, account_number: str, *, date_from: date, date_to: date) -> list[BankStatementMovement]:
        movements = self.parse(self.csv_content)
        return [movement for movement in movements if date_from <= movement.fecha <= date_to]

    def parse(self, csv_content: str) -> list[BankStatementMovement]:
        reader = csv.DictReader(io.StringIO(csv_content))
        fieldnames = set(reader.fieldnames or [])
        missing = self.REQUIRED_COLUMNS - fieldnames
        if missing:
            raise BankingProviderError(f"Estado bancario CSV inválido; faltan columnas: {', '.join(sorted(missing))}")
        return [self._movement_from_row(row) for row in reader]

    def _movement_from_row(self, row: dict[str, str]) -> BankStatementMovement:
        try:
            amount = Decimal(row["monto"])
        except (InvalidOperation, KeyError) as exc:
            raise BankingProviderError("Monto bancario inválido") from exc
        tipo = row["tipo"].upper()
        if tipo not in {"CARGO", "ABONO"}:
            raise BankingProviderError("Tipo de movimiento bancario inválido")
        try:
            movement_date = date.fromisoformat(row["fecha"])
        except (KeyError, ValueError) as exc:
            raise BankingProviderError("Fecha bancaria inválida") from exc
        return BankStatementMovement(
            fecha=movement_date,
            referencia=row["referencia"],
            descripcion=row.get("descripcion") or None,
            monto=amount,
            tipo=tipo,
        )


class HttpBankStatementProvider(BankStatementProvider):
    """HTTP adapter for bank statement APIs behind a normalized contract."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not base_url:
            raise BankingProviderError("BANKING_API_URL es obligatorio para el proveedor HTTP")
        if not api_key:
            raise BankingProviderError("BANKING_API_KEY es obligatorio para el proveedor HTTP")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def fetch_statement(self, account_number: str, *, date_from: date, date_to: date) -> list[BankStatementMovement]:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._headers(),
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.get(
                    f"/accounts/{account_number}/statement",
                    params={"date_from": date_from.isoformat(), "date_to": date_to.isoformat()},
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise BankingProviderError(
                f"Proveedor bancario respondió {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:
            raise BankingProviderError(f"Error al comunicarse con proveedor bancario: {exc}") from exc
        return self._movements_from_response(payload)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

    def _movements_from_response(self, payload: dict) -> list[BankStatementMovement]:
        items = payload.get("movements")
        if not isinstance(items, list):
            raise BankingProviderError("Respuesta bancaria inválida: se requiere lista 'movements'")
        movements: list[BankStatementMovement] = []
        for item in items:
            try:
                movements.append(
                    BankStatementMovement(
                        fecha=date.fromisoformat(item["fecha"]),
                        referencia=item["referencia"],
                        descripcion=item.get("descripcion"),
                        monto=Decimal(str(item["monto"])),
                        tipo=item["tipo"].upper(),
                    )
                )
            except (KeyError, InvalidOperation, ValueError) as exc:
                raise BankingProviderError("Movimiento bancario remoto inválido") from exc
            if movements[-1].tipo not in {"CARGO", "ABONO"}:
                raise BankingProviderError("Tipo de movimiento bancario remoto inválido")
        return movements


def get_bank_statement_provider(name: str, *, csv_content: str | None = None) -> BankStatementProvider:
    provider_name = (name or settings.BANKING_PROVIDER).upper()
    if provider_name == "CSV":
        if csv_content is None:
            raise BankingProviderError("Se requiere contenido CSV para el proveedor CSV")
        return CsvBankStatementProvider(csv_content)
    if provider_name in {"HTTP", "API"}:
        return HttpBankStatementProvider(
            settings.BANKING_API_URL,
            settings.BANKING_API_KEY,
            settings.BANKING_TIMEOUT_SECONDS,
        )
    raise ValueError(f"Proveedor bancario no soportado: {name}")
