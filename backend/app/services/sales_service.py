from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.producto import Producto
from app.models.venta import Cliente, Paciente, PagoVenta, RecetaOptica, Venta, VentaLinea
from app.schemas.outbox import OutboxEventCreate
from app.schemas.ventas import VentaCreate
from app.services.accounting_engine import AccountingEngine
from app.services.inventory_service import InventoryService
from app.services.outbox_service import OutboxService


class SalesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_venta(self, *, empresa_id: UUID, payload: VentaCreate) -> Venta:
        subtotal = sum((linea.importe for linea in payload.lineas), Decimal("0"))
        total = subtotal + payload.impuestos
        pagos_total = sum((pago.monto for pago in payload.pagos), Decimal("0"))
        if payload.pagos and pagos_total != total:
            raise ValueError("El total de pagos debe ser igual al total de la venta")

        cliente = await self._resolver_cliente(empresa_id, payload)
        paciente = await self._resolver_paciente(empresa_id, cliente.id, payload)
        receta = await self._resolver_receta(empresa_id, paciente.id if paciente else None, payload)

        venta = Venta(
            empresa_id=empresa_id,
            sucursal_id=payload.sucursal_id,
            cliente_id=cliente.id,
            paciente_id=paciente.id if paciente else None,
            receta_id=receta.id if receta else payload.receta_id,
            folio=payload.folio,
            estado="BORRADOR",
            subtotal=subtotal,
            impuestos=payload.impuestos,
            total=total,
            costo_total=Decimal("0"),
        )
        self.db.add(venta)
        await self.db.flush()

        for linea in payload.lineas:
            producto = await self._get_producto(empresa_id, linea.producto_id)
            venta.lineas.append(
                VentaLinea(
                    producto_id=producto.id,
                    descripcion=linea.descripcion or producto.nombre,
                    cantidad=linea.cantidad,
                    precio_unitario=linea.precio_unitario,
                    descuento=linea.descuento,
                    importe=linea.importe,
                    costo_total=Decimal("0"),
                )
            )
        for pago in payload.pagos:
            venta.pagos.append(PagoVenta(**pago.model_dump()))
        await self.db.flush()
        return venta

    async def confirmar_venta(
        self,
        *,
        empresa_id: UUID,
        venta_id: UUID,
        cuenta_cobro: str = "102.01",
        cuenta_ingresos: str = "401.01",
        cuenta_costo_ventas: str = "501.01",
        cuenta_inventario: str = "115.01",
    ) -> Venta:
        async with self.db.begin_nested():
            venta = await self._get_venta_for_update(empresa_id, venta_id)
            if venta.estado != "BORRADOR":
                raise ValueError("Solo una venta en BORRADOR puede confirmarse")
            if not venta.lineas:
                raise ValueError("La venta requiere al menos una línea")
            pagos_total = sum((pago.monto for pago in venta.pagos), Decimal("0"))
            if pagos_total != venta.total:
                raise ValueError("La venta requiere pagos por el total para confirmarse")

            inventory = InventoryService(self.db)
            costo_total = Decimal("0")
            for linea in venta.lineas:
                producto = await self._get_producto(empresa_id, linea.producto_id)
                if producto.es_servicio:
                    continue
                _, costo_linea = await inventory.salida_peps(
                    empresa_id=empresa_id,
                    sucursal_id=venta.sucursal_id,
                    producto_id=linea.producto_id,
                    cantidad=linea.cantidad,
                    origen="VENTA",
                    referencia=venta.folio,
                )
                linea.costo_total = costo_linea
                costo_total += costo_linea

            asiento = await AccountingEngine(self.db).handle_venta_confirmada(
                empresa_id=empresa_id,
                fecha=(venta.fecha or datetime.now(timezone.utc)).date(),
                referencia=venta.folio,
                total=venta.total,
                costo=costo_total,
                cuenta_cobro=cuenta_cobro,
                cuenta_ingresos=cuenta_ingresos,
                cuenta_costo_ventas=cuenta_costo_ventas,
                cuenta_inventario=cuenta_inventario,
            )
            venta.costo_total = costo_total
            venta.asiento_id = asiento.id
            venta.estado = "CONFIRMADA"
            await OutboxService(self.db).enqueue(
                empresa_id=empresa_id,
                payload=OutboxEventCreate(
                    aggregate_type="Venta",
                    aggregate_id=str(venta.id),
                    event_type="VentaConfirmada",
                    payload={"venta_id": str(venta.id), "folio": venta.folio, "total": str(venta.total), "costo_total": str(costo_total)},
                    idempotency_key=f"venta:{venta.id}:confirmada",
                ),
            )
            await self.db.flush()
        return await self.obtener_venta(empresa_id=empresa_id, venta_id=venta_id)

    async def obtener_venta(self, *, empresa_id: UUID, venta_id: UUID) -> Venta:
        result = await self.db.execute(
            select(Venta)
            .options(selectinload(Venta.lineas), selectinload(Venta.pagos))
            .where(Venta.empresa_id == empresa_id, Venta.id == venta_id)
        )
        venta = result.scalar_one_or_none()
        if venta is None:
            raise ValueError("Venta inexistente")
        return venta

    async def listar_ventas(self, *, empresa_id: UUID, skip: int = 0, limit: int = 50) -> list[Venta]:
        result = await self.db.execute(
            select(Venta)
            .options(selectinload(Venta.lineas), selectinload(Venta.pagos))
            .where(Venta.empresa_id == empresa_id)
            .order_by(Venta.fecha.desc(), Venta.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def _resolver_cliente(self, empresa_id: UUID, payload: VentaCreate) -> Cliente:
        if payload.cliente_id:
            cliente = await self.db.get(Cliente, payload.cliente_id)
            if cliente is None or cliente.empresa_id != empresa_id:
                raise ValueError("Cliente inexistente para la empresa")
            return cliente
        cliente = Cliente(empresa_id=empresa_id, **payload.cliente.model_dump())
        self.db.add(cliente)
        await self.db.flush()
        return cliente

    async def _resolver_paciente(self, empresa_id: UUID, cliente_id: UUID, payload: VentaCreate) -> Paciente | None:
        if payload.paciente_id:
            paciente = await self.db.get(Paciente, payload.paciente_id)
            if paciente is None or paciente.empresa_id != empresa_id or paciente.cliente_id != cliente_id:
                raise ValueError("Paciente inexistente para el cliente")
            return paciente
        if payload.paciente is None:
            return None
        data = payload.paciente.model_dump(exclude={"cliente_id"})
        paciente = Paciente(empresa_id=empresa_id, cliente_id=cliente_id, **data)
        self.db.add(paciente)
        await self.db.flush()
        return paciente

    async def _resolver_receta(self, empresa_id: UUID, paciente_id: UUID | None, payload: VentaCreate) -> RecetaOptica | None:
        if payload.receta_id:
            receta = await self.db.get(RecetaOptica, payload.receta_id)
            if receta is None or receta.empresa_id != empresa_id:
                raise ValueError("Receta óptica inexistente para la empresa")
            return receta
        if payload.receta is None:
            return None
        if paciente_id is None:
            raise ValueError("Se requiere paciente para capturar receta óptica")
        data = payload.receta.model_dump(exclude={"paciente_id"})
        receta = RecetaOptica(empresa_id=empresa_id, paciente_id=paciente_id, **data)
        self.db.add(receta)
        await self.db.flush()
        return receta

    async def _get_producto(self, empresa_id: UUID, producto_id: UUID) -> Producto:
        producto = await self.db.get(Producto, producto_id)
        if producto is None or producto.empresa_id != empresa_id:
            raise ValueError("Producto inexistente para la empresa")
        return producto

    async def _get_venta_for_update(self, empresa_id: UUID, venta_id: UUID) -> Venta:
        result = await self.db.execute(
            select(Venta)
            .options(selectinload(Venta.lineas), selectinload(Venta.pagos))
            .where(Venta.empresa_id == empresa_id, Venta.id == venta_id)
            .with_for_update()
        )
        venta = result.scalar_one_or_none()
        if venta is None:
            raise ValueError("Venta inexistente")
        return venta
