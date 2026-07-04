from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.configuracion import Impuesto, ReglaContable, SerieFolio, TipoCambio
from app.schemas.configuracion import ImpuestoCreate, ReglaContableCreate, SerieFolioCreate, TipoCambioCreate


class ConfigurationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_impuesto(self, *, empresa_id: UUID, payload: ImpuestoCreate) -> Impuesto:
        impuesto = Impuesto(empresa_id=empresa_id, **payload.model_dump())
        self.db.add(impuesto)
        await self.db.flush()
        return impuesto

    async def listar_impuestos(self, *, empresa_id: UUID, skip: int = 0, limit: int = 100) -> list[Impuesto]:
        result = await self.db.execute(select(Impuesto).where(Impuesto.empresa_id == empresa_id).order_by(Impuesto.codigo.asc()).offset(skip).limit(limit))
        return result.scalars().all()

    async def crear_serie(self, *, empresa_id: UUID, payload: SerieFolioCreate) -> SerieFolio:
        serie = SerieFolio(empresa_id=empresa_id, **payload.model_dump())
        self.db.add(serie)
        await self.db.flush()
        return serie

    async def siguiente_folio(self, *, empresa_id: UUID, documento: str, serie: str) -> str:
        result = await self.db.execute(
            select(SerieFolio)
            .where(SerieFolio.empresa_id == empresa_id, SerieFolio.documento == documento, SerieFolio.serie == serie)
            .with_for_update()
        )
        folio = result.scalar_one_or_none()
        if folio is None:
            raise ValueError("Serie de folios inexistente")
        folio.folio_actual = Decimal(folio.folio_actual) + Decimal("1")
        await self.db.flush()
        return folio.formato.format(serie=folio.serie, folio=int(folio.folio_actual), documento=folio.documento)

    async def crear_tipo_cambio(self, *, empresa_id: UUID, payload: TipoCambioCreate) -> TipoCambio:
        tipo_cambio = TipoCambio(
            empresa_id=empresa_id,
            moneda_origen=payload.moneda_origen.upper(),
            moneda_destino=payload.moneda_destino.upper(),
            fecha=payload.fecha,
            tasa=payload.tasa,
            fuente=payload.fuente,
        )
        self.db.add(tipo_cambio)
        await self.db.flush()
        return tipo_cambio

    async def obtener_tipo_cambio(self, *, empresa_id: UUID, moneda_origen: str, moneda_destino: str) -> TipoCambio:
        result = await self.db.execute(
            select(TipoCambio)
            .where(
                TipoCambio.empresa_id == empresa_id,
                TipoCambio.moneda_origen == moneda_origen.upper(),
                TipoCambio.moneda_destino == moneda_destino.upper(),
            )
            .order_by(TipoCambio.fecha.desc())
            .limit(1)
        )
        tipo_cambio = result.scalar_one_or_none()
        if tipo_cambio is None:
            raise ValueError("Tipo de cambio inexistente")
        return tipo_cambio

    async def crear_regla_contable(self, *, empresa_id: UUID, payload: ReglaContableCreate) -> ReglaContable:
        regla = ReglaContable(empresa_id=empresa_id, **payload.model_dump())
        self.db.add(regla)
        await self.db.flush()
        return regla

    async def listar_reglas_contables(self, *, empresa_id: UUID, skip: int = 0, limit: int = 100) -> list[ReglaContable]:
        result = await self.db.execute(select(ReglaContable).where(ReglaContable.empresa_id == empresa_id).order_by(ReglaContable.evento.asc()).offset(skip).limit(limit))
        return result.scalars().all()
