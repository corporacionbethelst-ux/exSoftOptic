from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import AsientoContable, CuentaContable, LineaAsientoContable
from app.services.accounting_period_service import AccountingPeriodService


@dataclass(frozen=True)
class AccountingLineInput:
    cuenta_codigo: str
    descripcion: str
    debe: Decimal = Decimal("0")
    haber: Decimal = Decimal("0")


class AccountingEngine:
    """Motor transaccional de doble entrada para eventos de dominio."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_journal_entry(
        self,
        *,
        empresa_id: UUID,
        fecha: date,
        descripcion: str,
        origen: str,
        referencia: str | None,
        lines: list[AccountingLineInput],
        moneda: str = "MXN",
    ) -> AsientoContable:
        if len(lines) < 2:
            raise ValueError("Un asiento contable requiere al menos dos líneas")
        total_debe = sum((line.debe for line in lines), Decimal("0"))
        total_haber = sum((line.haber for line in lines), Decimal("0"))
        if total_debe <= 0 or total_debe != total_haber:
            raise ValueError("Asiento descuadrado: debe y haber deben ser iguales y positivos")

        await AccountingPeriodService(self.db).assert_fecha_contabilizable(empresa_id=empresa_id, fecha=fecha)

        codes = {line.cuenta_codigo for line in lines}
        result = await self.db.execute(
            select(CuentaContable).where(CuentaContable.empresa_id == empresa_id, CuentaContable.codigo.in_(codes))
        )
        accounts = {account.codigo: account for account in result.scalars().all()}
        missing = codes - set(accounts)
        if missing:
            raise ValueError(f"Cuentas contables inexistentes: {', '.join(sorted(missing))}")

        asiento = AsientoContable(
            empresa_id=empresa_id,
            fecha=fecha,
            descripcion=descripcion,
            origen=origen,
            referencia=referencia,
            moneda=moneda,
        )
        asiento.lineas = [
            LineaAsientoContable(
                cuenta_id=accounts[line.cuenta_codigo].id,
                descripcion=line.descripcion,
                debe=line.debe,
                haber=line.haber,
            )
            for line in lines
        ]
        self.db.add(asiento)
        await self.db.flush()
        return asiento

    async def handle_venta_confirmada(
        self,
        *,
        empresa_id: UUID,
        fecha: date,
        referencia: str,
        total: Decimal,
        costo: Decimal,
        cuenta_cobro: str = "102.01",
        cuenta_ingresos: str = "401.01",
        cuenta_costo_ventas: str = "501.01",
        cuenta_inventario: str = "115.01",
    ) -> AsientoContable:
        return await self.create_journal_entry(
            empresa_id=empresa_id,
            fecha=fecha,
            descripcion=f"Venta confirmada {referencia}",
            origen="VENTA_CONFIRMADA",
            referencia=referencia,
            lines=[
                AccountingLineInput(cuenta_cobro, "Cargo por cobro/CxC", debe=total),
                AccountingLineInput(cuenta_ingresos, "Ingreso por venta", haber=total),
                AccountingLineInput(cuenta_costo_ventas, "Costo de venta", debe=costo),
                AccountingLineInput(cuenta_inventario, "Salida de inventario", haber=costo),
            ],
        )

    async def handle_devolucion_venta(
        self,
        *,
        empresa_id: UUID,
        fecha: date,
        referencia: str,
        total: Decimal,
        costo: Decimal,
        cuenta_cobro: str = "102.01",
        cuenta_ingresos: str = "401.01",
        cuenta_costo_ventas: str = "501.01",
        cuenta_inventario: str = "115.01",
    ) -> AsientoContable:
        return await self.create_journal_entry(
            empresa_id=empresa_id,
            fecha=fecha,
            descripcion=f"Devolución de venta {referencia}",
            origen="DEVOLUCION_VENTA",
            referencia=referencia,
            lines=[
                AccountingLineInput(cuenta_ingresos, "Reverso de ingreso por devolución", debe=total),
                AccountingLineInput(cuenta_cobro, "Reverso de cobro/CxC", haber=total),
                AccountingLineInput(cuenta_inventario, "Entrada de inventario por devolución", debe=costo),
                AccountingLineInput(cuenta_costo_ventas, "Reverso de costo de venta", haber=costo),
            ],
        )

    async def handle_compra_recibida(
        self,
        *,
        empresa_id: UUID,
        fecha: date,
        referencia: str,
        total: Decimal,
        cuenta_inventario: str = "115.01",
        cuenta_cxp: str = "201.01",
    ) -> AsientoContable:
        return await self.create_journal_entry(
            empresa_id=empresa_id,
            fecha=fecha,
            descripcion=f"Recepción de compra {referencia}",
            origen="COMPRA_RECIBIDA",
            referencia=referencia,
            lines=[
                AccountingLineInput(cuenta_inventario, "Entrada de inventario", debe=total),
                AccountingLineInput(cuenta_cxp, "Cuenta por pagar proveedor", haber=total),
            ],
        )

    async def handle_nomina_generada(
        self,
        *,
        empresa_id: UUID,
        fecha: date,
        referencia: str,
        total_percepciones: Decimal,
        total_deducciones: Decimal,
        total_neto: Decimal,
        cuenta_gasto_sueldos: str = "601.01",
        cuenta_bancos: str = "102.01",
        cuenta_retenciones: str = "216.01",
    ) -> AsientoContable:
        lines = [
            AccountingLineInput(cuenta_gasto_sueldos, "Gasto de nómina", debe=total_percepciones),
            AccountingLineInput(cuenta_bancos, "Pago neto de nómina", haber=total_neto),
        ]
        if total_deducciones > 0:
            lines.append(AccountingLineInput(cuenta_retenciones, "Retenciones de nómina", haber=total_deducciones))
        return await self.create_journal_entry(
            empresa_id=empresa_id,
            fecha=fecha,
            descripcion=f"Nómina generada {referencia}",
            origen="NOMINA_GENERADA",
            referencia=referencia,
            lines=lines,
        )
