from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_permissions, require_sucursal_scope
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.configuracion import ImpuestoCreate, ImpuestoResponse, ReglaContableCreate, ReglaContableResponse, SerieFolioCreate, SerieFolioResponse, TipoCambioCreate, TipoCambioResponse
from app.services.configuration_service import ConfigurationService
from app.services.secured_audit import audit_user_action

router = APIRouter()


@router.post("/impuestos", response_model=ImpuestoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["configuracion.impuestos.crear"]))])
async def crear_impuesto(payload: ImpuestoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    impuesto = await ConfigurationService(db).crear_impuesto(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="CONFIG_IMPUESTO_CREAR", entidad="Impuesto", entidad_id=impuesto.id, payload={"codigo": impuesto.codigo, "tasa": str(impuesto.tasa)})
    return impuesto


@router.get("/impuestos", response_model=list[ImpuestoResponse], dependencies=[Depends(require_permissions(["configuracion.impuestos.leer"]))])
async def listar_impuestos(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ConfigurationService(db).listar_impuestos(empresa_id=current_user.empresa_id, skip=skip, limit=limit)


@router.post("/series", response_model=SerieFolioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["configuracion.series.crear"]))])
async def crear_serie(payload: SerieFolioCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    require_sucursal_scope(payload.sucursal_id, current_user)
    serie = await ConfigurationService(db).crear_serie(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="CONFIG_SERIE_CREAR", entidad="SerieFolio", entidad_id=serie.id, payload={"documento": serie.documento, "serie": serie.serie})
    return serie


@router.post("/series/{documento}/{serie}/siguiente", dependencies=[Depends(require_permissions(["configuracion.series.usar"]))])
async def siguiente_folio(documento: str, serie: str, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        folio = await ConfigurationService(db).siguiente_folio(empresa_id=current_user.empresa_id, documento=documento, serie=serie)
        await audit_user_action(db, current_user=current_user, accion="CONFIG_SERIE_CONSUMIR", entidad="SerieFolio", payload={"documento": documento, "serie": serie, "folio": folio})
        return {"folio": folio}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/tipos-cambio", response_model=TipoCambioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["configuracion.tipos_cambio.crear"]))])
async def crear_tipo_cambio(payload: TipoCambioCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    tipo_cambio = await ConfigurationService(db).crear_tipo_cambio(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="CONFIG_TIPO_CAMBIO_CREAR", entidad="TipoCambio", entidad_id=tipo_cambio.id, payload={"moneda_origen": tipo_cambio.moneda_origen, "moneda_destino": tipo_cambio.moneda_destino, "tasa": str(tipo_cambio.tasa)})
    return tipo_cambio


@router.get("/tipos-cambio", response_model=TipoCambioResponse, dependencies=[Depends(require_permissions(["configuracion.tipos_cambio.leer"]))])
async def obtener_tipo_cambio(moneda_origen: str = Query(..., min_length=3, max_length=3), moneda_destino: str = Query(..., min_length=3, max_length=3), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    try:
        return await ConfigurationService(db).obtener_tipo_cambio(empresa_id=current_user.empresa_id, moneda_origen=moneda_origen, moneda_destino=moneda_destino)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/reglas-contables", response_model=ReglaContableResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(["configuracion.reglas_contables.crear"]))])
async def crear_regla_contable(payload: ReglaContableCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    regla = await ConfigurationService(db).crear_regla_contable(empresa_id=current_user.empresa_id, payload=payload)
    await audit_user_action(db, current_user=current_user, accion="CONFIG_REGLA_CONTABLE_CREAR", entidad="ReglaContable", entidad_id=regla.id, payload={"evento": regla.evento})
    return regla


@router.get("/reglas-contables", response_model=list[ReglaContableResponse], dependencies=[Depends(require_permissions(["configuracion.reglas_contables.leer"]))])
async def listar_reglas_contables(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    return await ConfigurationService(db).listar_reglas_contables(empresa_id=current_user.empresa_id, skip=skip, limit=limit)
