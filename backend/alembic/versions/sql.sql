-- ============================================================================
-- SISTEMA INTEGRAL DE GESTIÓN PARA ÓPTICAS - VERSIÓN EMPRESARIAL
-- Versión: 2.0.0
-- Fecha: 2026-06-18
-- Módulos: Contabilidad, Compras, Ventas, Inventario, Tesorería, 
--          Activos Fijos, Nómina, Fiscal, Clínico, CRM
-- ============================================================================

-- ============================================================================
-- EXTENSIONES
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- ============================================================================
-- FUNCIONES AUXILIARES
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_auditoria()
RETURNS TRIGGER AS $$
DECLARE
    usuario_actual UUID;
BEGIN
    usuario_actual := NULLIF(current_setting('app.current_user_id', true), '')::UUID;
    
    INSERT INTO auditoria (
        usuario_id, accion, modulo, entidad, entidad_id,
        datos_anteriores, datos_nuevos, ip_address
    ) VALUES (
        usuario_actual, TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME,
        COALESCE((NEW).id, (OLD).id),
        CASE WHEN TG_OP != 'INSERT' THEN to_jsonb(OLD) END,
        CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) END,
        inet_client_addr()
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MÓDULO 1: CORE SYSTEM (Configuración Base)
-- ============================================================================

-- EMPRESAS (Multi-empresa)
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    razon_social VARCHAR(200) NOT NULL,
    nombre_comercial VARCHAR(150),
    rfc VARCHAR(20) UNIQUE NOT NULL,
    regimen_fiscal VARCHAR(50) NOT NULL,
    codigo_postal VARCHAR(10) NOT NULL,
    representante_legal VARCHAR(150),
    logo_url TEXT,
    configuracion_contable JSONB DEFAULT '{}',
    serie_factura VARCHAR(10) DEFAULT 'A',
    folio_actual INTEGER DEFAULT 0,
    moneda_base VARCHAR(3) DEFAULT 'MXN',
    esta_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SUCURSALES
CREATE TABLE sucursales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    rfc VARCHAR(20),
    codigo_postal VARCHAR(10),
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    pais VARCHAR(50) DEFAULT 'México',
    es_principal BOOLEAN DEFAULT FALSE,
    esta_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, codigo)
);

-- USUARIOS
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    sucursal_id UUID REFERENCES sucursales(id),
    esta_activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MÓDULO 2: CONTABILIDAD COMPLETA
-- ============================================================================

-- PLAN DE CUENTAS CONTABLES
CREATE TABLE cuentas_contables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    tipo_cuenta VARCHAR(50) NOT NULL, -- ACTIVO, PASIVO, CAPITAL, INGRESO, EGRESO
    naturaleza VARCHAR(20) NOT NULL, -- DEUDORA, ACREEDORA
    nivel INTEGER NOT NULL DEFAULT 1,
    cuenta_padre_id UUID REFERENCES cuentas_contables(id),
    es_movimiento BOOLEAN DEFAULT FALSE, -- Si acepta movimientos
    requiere_auxiliar BOOLEAN DEFAULT FALSE, -- Si requiere subcuenta
    esta_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, codigo)
);

CREATE INDEX idx_cuentas_codigo ON cuentas_contables(empresa_id, codigo);
CREATE INDEX idx_cuentas_tipo ON cuentas_contables(tipo_cuenta);
CREATE INDEX idx_cuentas_padre ON cuentas_contables(cuenta_padre_id);

-- AUXILIARES DE CUENTAS (Subcuentas)
CREATE TABLE auxiliares_contables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id UUID NOT NULL REFERENCES cuentas_contables(id),
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    tipo_auxiliar VARCHAR(50), -- CLIENTE, PROVEEDOR, BANCO, EMPLEADO
    referencia_id UUID, -- ID del cliente/proveedor/etc
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(cuenta_id, codigo)
);

-- PERIODOS CONTABLES
CREATE TABLE periodos_contables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    ejercicio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(30) DEFAULT 'ABIERTO', -- ABIERTO, CERRADO, AJUSTE
    UNIQUE(empresa_id, ejercicio, mes)
);

-- ASIENTOS CONTABLES (Cabecera)
CREATE TABLE asientos_contables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    periodo_id UUID NOT NULL REFERENCES periodos_contables(id),
    numero_asiento VARCHAR(30) NOT NULL,
    fecha_asiento DATE NOT NULL,
    concepto TEXT NOT NULL,
    tipo_asiento VARCHAR(50) NOT NULL, -- MANUAL, AUTOMATICO, AJUSTE, CIERRE
    referencia_tipo VARCHAR(50), -- VENTA, COMPRA, PAGO, COBRO, NOMINA
    referencia_id UUID,
    total_debe DECIMAL(15,2) DEFAULT 0,
    total_haber DECIMAL(15,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'CONTABILIZADO', -- BORRADOR, CONTABILIZADO, ANULADO
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, numero_asiento)
);

CREATE INDEX idx_asientos_fecha ON asientos_contables(fecha_asiento);
CREATE INDEX idx_asientos_referencia ON asientos_contables(referencia_tipo, referencia_id);

-- DETALLE DE ASIENTOS (Partidas)
CREATE TABLE partidas_contables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asiento_id UUID NOT NULL REFERENCES asientos_contables(id) ON DELETE CASCADE,
    cuenta_id UUID NOT NULL REFERENCES cuentas_contables(id),
    auxiliar_id UUID REFERENCES auxiliares_contables(id),
    concepto VARCHAR(500),
    debe DECIMAL(15,2) DEFAULT 0,
    haber DECIMAL(15,2) DEFAULT 0,
    moneda VARCHAR(3) DEFAULT 'MXN',
    tipo_cambio DECIMAL(10,4) DEFAULT 1.0
);

CREATE INDEX idx_partidas_asiento ON partidas_contables(asiento_id);
CREATE INDEX idx_partidas_cuenta ON partidas_contables(cuenta_id);

-- SALDOS DE CUENTAS (Por periodo)
CREATE TABLE saldos_contables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id UUID NOT NULL REFERENCES cuentas_contables(id),
    auxiliar_id UUID REFERENCES auxiliares_contables(id),
    periodo_id UUID NOT NULL REFERENCES periodos_contables(id),
    saldo_inicial DECIMAL(15,2) DEFAULT 0,
    movimientos_debe DECIMAL(15,2) DEFAULT 0,
    movimientos_haber DECIMAL(15,2) DEFAULT 0,
    saldo_final DECIMAL(15,2) DEFAULT 0,
    UNIQUE(cuenta_id, auxiliar_id, periodo_id)
);

-- LIBRO DIARIO (Vista)
CREATE VIEW v_libro_diario AS
SELECT 
    a.fecha_asiento,
    a.numero_asiento,
    a.concepto,
    c.codigo as cuenta_codigo,
    c.nombre as cuenta_nombre,
    p.concepto as partida_concepto,
    p.debe,
    p.haber
FROM asientos_contables a
JOIN partidas_contables p ON p.asiento_id = a.id
JOIN cuentas_contables c ON c.id = p.cuenta_id
WHERE a.estado = 'CONTABILIZADO'
ORDER BY a.fecha_asiento, a.numero_asiento;

-- BALANCE DE COMPROBACIÓN (Función)
CREATE OR REPLACE FUNCTION fn_balance_comprobacion(
    p_empresa_id UUID,
    p_periodo_id UUID
)
RETURNS TABLE (
    cuenta_codigo VARCHAR,
    cuenta_nombre VARCHAR,
    saldo_inicial DECIMAL,
    movimientos_debe DECIMAL,
    movimientos_haber DECIMAL,
    saldo_final DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.codigo,
        c.nombre,
        COALESCE(SUM(s.saldo_inicial), 0),
        COALESCE(SUM(s.movimientos_debe), 0),
        COALESCE(SUM(s.movimientos_haber), 0),
        COALESCE(SUM(s.saldo_final), 0)
    FROM cuentas_contables c
    LEFT JOIN saldos_contables s ON s.cuenta_id = c.id AND s.periodo_id = p_periodo_id
    WHERE c.empresa_id = p_empresa_id
        AND c.esta_activa = TRUE
    GROUP BY c.id, c.codigo, c.nombre
    ORDER BY c.codigo;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MÓDULO 3: PROVEEDORES Y CUENTAS POR PAGAR
-- ============================================================================

-- PROVEEDORES
CREATE TABLE proveedores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    codigo VARCHAR(20) NOT NULL,
    razon_social VARCHAR(200) NOT NULL,
    nombre_contacto VARCHAR(100),
    rfc VARCHAR(20),
    email VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    ciudad VARCHAR(100),
    codigo_postal VARCHAR(10),
    regimen_fiscal VARCHAR(50),
    uso_cfdi VARCHAR(10) DEFAULT 'G03',
    dias_credito INTEGER DEFAULT 0,
    limite_credito DECIMAL(15,2) DEFAULT 0,
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    auxiliar_contable_id UUID REFERENCES auxiliares_contables(id),
    es_laboratorio BOOLEAN DEFAULT FALSE,
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, codigo)
);

CREATE INDEX idx_proveedores_codigo ON proveedores(empresa_id, codigo);
CREATE INDEX idx_proveedores_rfc ON proveedores(rfc);

-- SOLICITUDES DE COMPRA
CREATE TABLE solicitudes_compra (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    numero_solicitud VARCHAR(30) NOT NULL,
    fecha_solicitud DATE NOT NULL DEFAULT CURRENT_DATE,
    solicitante_id UUID NOT NULL REFERENCES usuarios(id),
    prioridad VARCHAR(20) DEFAULT 'NORMAL', -- BAJA, NORMAL, ALTA, URGENTE
    estado VARCHAR(30) DEFAULT 'SOLICITADA', -- SOLICITADA, APROBADA, RECHAZADA, CONVERTIDA
    observaciones TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE SOLICITUDES DE COMPRA
CREATE TABLE solicitudes_compra_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id UUID NOT NULL REFERENCES solicitudes_compra(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL,
    cantidad_solicitada DECIMAL(15,3) NOT NULL,
    cantidad_aprobada DECIMAL(15,3) DEFAULT 0,
    justificacion TEXT
);

-- ÓRDENES DE COMPRA
CREATE TABLE ordenes_compra (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    proveedor_id UUID NOT NULL REFERENCES proveedores(id),
    solicitud_id UUID REFERENCES solicitudes_compra(id),
    numero_orden VARCHAR(30) NOT NULL,
    fecha_orden DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_entrega_estimada DATE,
    condiciones_pago VARCHAR(100),
    metodo_envio VARCHAR(50),
    subtotal DECIMAL(15,2) DEFAULT 0,
    impuestos DECIMAL(15,2) DEFAULT 0,
    descuento DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'BORRADOR', -- BORRADOR, ENVIADA, PARCIAL, RECIBIDA, CANCELADA
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, numero_orden)
);

CREATE INDEX idx_ordenes_compra_proveedor ON ordenes_compra(proveedor_id);
CREATE INDEX idx_ordenes_compra_estado ON ordenes_compra(estado);

-- DETALLE ÓRDENES DE COMPRA
CREATE TABLE ordenes_compra_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orden_id UUID NOT NULL REFERENCES ordenes_compra(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL,
    descripcion VARCHAR(500) NOT NULL,
    cantidad_solicitada DECIMAL(15,3) NOT NULL,
    cantidad_recibida DECIMAL(15,3) DEFAULT 0,
    cantidad_pendiente DECIMAL(15,3) GENERATED ALWAYS AS (cantidad_solicitada - cantidad_recibida) STORED,
    precio_unitario DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    subtotal DECIMAL(15,2) NOT NULL,
    impuestos DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL,
    fecha_entrega_esperada DATE
);

-- RECEPCIONES DE MERCANCÍA
CREATE TABLE recepciones_mercancia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    orden_compra_id UUID NOT NULL REFERENCES ordenes_compra(id),
    proveedor_id UUID NOT NULL REFERENCES proveedores(id),
    numero_recepcion VARCHAR(30) NOT NULL,
    fecha_recepcion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    numero_remision VARCHAR(50),
    numero_factura VARCHAR(50),
    fecha_factura DATE,
    subtotal DECIMAL(15,2) DEFAULT 0,
    impuestos DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'RECIBIDA', -- RECIBIDA, EN_REVISION, ACEPTADA, RECHAZADA, DEVUELTA
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, numero_recepcion)
);

-- DETALLE RECEPCIONES
CREATE TABLE recepciones_mercancia_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recepcion_id UUID NOT NULL REFERENCES recepciones_mercancia(id) ON DELETE CASCADE,
    orden_compra_detalle_id UUID NOT NULL REFERENCES ordenes_compra_detalle(id),
    producto_id UUID NOT NULL,
    cantidad_recibida DECIMAL(15,3) NOT NULL,
    cantidad_aceptada DECIMAL(15,3) NOT NULL,
    cantidad_rechazada DECIMAL(15,3) DEFAULT 0,
    lote VARCHAR(50),
    fecha_caducidad DATE,
    costo_unitario DECIMAL(15,2) NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL
);

-- FACTURAS DE PROVEEDORES (Cuentas por Pagar)
CREATE TABLE facturas_proveedor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    proveedor_id UUID NOT NULL REFERENCES proveedores(id),
    recepcion_id UUID REFERENCES recepciones_mercancia(id),
    numero_factura VARCHAR(50) NOT NULL,
    serie_factura VARCHAR(10),
    fecha_factura DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    iva DECIMAL(15,2) DEFAULT 0,
    iePS DECIMAL(15,2) DEFAULT 0,
    retencion_isr DECIMAL(15,2) DEFAULT 0,
    retencion_iva DECIMAL(15,2) DEFAULT 0,
    descuento DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL,
    monto_pagado DECIMAL(15,2) DEFAULT 0,
    saldo_pendiente DECIMAL(15,2) GENERATED ALWAYS AS (total - monto_pagado) STORED,
    moneda VARCHAR(3) DEFAULT 'MXN',
    tipo_cambio DECIMAL(10,4) DEFAULT 1.0,
    uuid_cfdi VARCHAR(50),
    estado VARCHAR(30) DEFAULT 'REGISTRADA', -- REGISTRADA, PARCIAL, PAGADA, CANCELADA, VENCIDA
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    auxiliar_contable_id UUID REFERENCES auxiliares_contables(id),
    asiento_contable_id UUID REFERENCES asientos_contables(id),
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_facturas_prov_numero ON facturas_proveedor(numero_factura);
CREATE INDEX idx_facturas_prov_proveedor ON facturas_proveedor(proveedor_id);
CREATE INDEX idx_facturas_prov_vencimiento ON facturas_proveedor(fecha_vencimiento);
CREATE INDEX idx_facturas_prov_estado ON facturas_proveedor(estado);

-- PAGOS A PROVEEDORES
CREATE TABLE pagos_proveedor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    proveedor_id UUID NOT NULL REFERENCES proveedores(id),
    numero_pago VARCHAR(30) NOT NULL,
    fecha_pago TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    monto DECIMAL(15,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'MXN',
    tipo_cambio DECIMAL(10,4) DEFAULT 1.0,
    metodo_pago VARCHAR(50) NOT NULL, -- EFECTIVO, TRANSFERENCIA, CHEQUE, TARJETA
    referencia VARCHAR(100),
    banco_id UUID,
    cuenta_bancaria_id UUID,
    estado VARCHAR(30) DEFAULT 'APLICADO', -- PENDIENTE, APLICADO, CANCELADO
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- APLICACIÓN DE PAGOS A FACTURAS
CREATE TABLE pagos_facturas_proveedor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pago_id UUID NOT NULL REFERENCES pagos_proveedor(id) ON DELETE CASCADE,
    factura_id UUID NOT NULL REFERENCES facturas_proveedor(id),
    monto_aplicado DECIMAL(15,2) NOT NULL,
    fecha_aplicacion TIMESTAMPTZ DEFAULT NOW()
);

-- NOTAS DE CRÉDITO DE PROVEEDORES (Devoluciones)
CREATE TABLE notas_credito_proveedor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    proveedor_id UUID NOT NULL REFERENCES proveedores(id),
    factura_id UUID REFERENCES facturas_proveedor(id),
    numero_nota VARCHAR(50) NOT NULL,
    fecha_nota DATE NOT NULL,
    motivo TEXT NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    iva DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL,
    estado VARCHAR(30) DEFAULT 'REGISTRADA', -- REGISTRADA, APLICADA, CANCELADA
    uuid_cfdi VARCHAR(50),
    asiento_contable_id UUID REFERENCES asientos_contables(id),
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE NOTAS DE CRÉDITO
CREATE TABLE notas_credito_proveedor_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nota_id UUID NOT NULL REFERENCES notas_credito_proveedor(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL,
    cantidad DECIMAL(15,3) NOT NULL,
    precio_unitario DECIMAL(15,2) NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL
);

-- ============================================================================
-- MÓDULO 4: CLIENTES Y CUENTAS POR COBRAR
-- ============================================================================

-- CLIENTES
CREATE TABLE clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    codigo VARCHAR(20) NOT NULL,
    tipo_persona VARCHAR(20) DEFAULT 'FISICA',
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(50),
    apellido_materno VARCHAR(50),
    razon_social VARCHAR(200),
    rfc VARCHAR(20),
    curp VARCHAR(18),
    email VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    codigo_postal VARCHAR(10),
    regimen_fiscal VARCHAR(50),
    uso_cfdi VARCHAR(10) DEFAULT 'G03',
    dias_credito INTEGER DEFAULT 0,
    limite_credito DECIMAL(15,2) DEFAULT 0,
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    auxiliar_contable_id UUID REFERENCES auxiliares_contables(id),
    nivel_cliente VARCHAR(20) DEFAULT 'REGULAR',
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, codigo)
);

CREATE INDEX idx_clientes_codigo ON clientes(empresa_id, codigo);
CREATE INDEX idx_clientes_rfc ON clientes(rfc);

-- COTIZACIONES
CREATE TABLE cotizaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    numero_cotizacion VARCHAR(30) NOT NULL,
    fecha_cotizacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vigencia DATE NOT NULL,
    subtotal DECIMAL(15,2) DEFAULT 0,
    impuestos DECIMAL(15,2) DEFAULT 0,
    descuento DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'EMITIDA', -- EMITIDA, APROBADA, RECHAZADA, CONVERTIDA, VENCIDA
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE COTIZACIONES
CREATE TABLE cotizaciones_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cotizacion_id UUID NOT NULL REFERENCES cotizaciones(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL,
    descripcion VARCHAR(500) NOT NULL,
    cantidad DECIMAL(15,3) NOT NULL,
    precio_unitario DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    subtotal DECIMAL(15,2) NOT NULL,
    impuestos DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL
);

-- FACTURAS DE VENTA (Cuentas por Cobrar)
CREATE TABLE facturas_venta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    cotizacion_id UUID REFERENCES cotizaciones(id),
    numero_factura VARCHAR(50) NOT NULL,
    serie_factura VARCHAR(10) NOT NULL,
    fecha_factura DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    metodo_pago VARCHAR(50) DEFAULT 'PUE', -- PUE, PPD
    forma_pago VARCHAR(50) DEFAULT 'EFECTIVO',
    subtotal DECIMAL(15,2) NOT NULL,
    iva DECIMAL(15,2) DEFAULT 0,
    iePS DECIMAL(15,2) DEFAULT 0,
    retencion_isr DECIMAL(15,2) DEFAULT 0,
    retencion_iva DECIMAL(15,2) DEFAULT 0,
    descuento DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL,
    monto_pagado DECIMAL(15,2) DEFAULT 0,
    saldo_pendiente DECIMAL(15,2) GENERATED ALWAYS AS (total - monto_pagado) STORED,
    moneda VARCHAR(3) DEFAULT 'MXN',
    tipo_cambio DECIMAL(10,4) DEFAULT 1.0,
    uuid_cfdi VARCHAR(50),
    sello_cfdi TEXT,
    qr_cfdi TEXT,
    fecha_timbrado TIMESTAMPTZ,
    estado VARCHAR(30) DEFAULT 'EMITIDA', -- EMITIDA, PARCIAL, PAGADA, CANCELADA, VENCIDA
    motivo_cancelacion TEXT,
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    auxiliar_contable_id UUID REFERENCES auxiliares_contables(id),
    asiento_contable_id UUID REFERENCES asientos_contables(id),
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_facturas_venta_numero ON facturas_venta(numero_factura);
CREATE INDEX idx_facturas_venta_cliente ON facturas_venta(cliente_id);
CREATE INDEX idx_facturas_venta_vencimiento ON facturas_venta(fecha_vencimiento);
CREATE INDEX idx_facturas_venta_estado ON facturas_venta(estado);
CREATE INDEX idx_facturas_venta_uuid ON facturas_venta(uuid_cfdi);

-- DETALLE FACTURAS DE VENTA
CREATE TABLE facturas_venta_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    factura_id UUID NOT NULL REFERENCES facturas_venta(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL,
    descripcion VARCHAR(500) NOT NULL,
    cantidad DECIMAL(15,3) NOT NULL,
    precio_unitario DECIMAL(15,2) NOT NULL,
    descuento DECIMAL(15,2) DEFAULT 0,
    subtotal DECIMAL(15,2) NOT NULL,
    impuestos DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL,
    costo_unitario DECIMAL(15,2) DEFAULT 0,
    costo_total DECIMAL(15,2) DEFAULT 0,
    unidad_clave VARCHAR(10) DEFAULT 'H87', -- Clave SAT
    producto_clave VARCHAR(20) DEFAULT '01010101' -- Clave producto SAT
);

-- NOTAS DE CRÉDITO DE CLIENTES (Devoluciones)
CREATE TABLE notas_credito_cliente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    factura_id UUID REFERENCES facturas_venta(id),
    numero_nota VARCHAR(50) NOT NULL,
    serie_nota VARCHAR(10) NOT NULL,
    fecha_nota DATE NOT NULL DEFAULT CURRENT_DATE,
    motivo TEXT NOT NULL,
    tipo_devolucion VARCHAR(50) NOT NULL, -- MERCANCIA_DEFECTUOSA, ERROR_FACTURACION, CANCELACION, OTRO
    subtotal DECIMAL(15,2) NOT NULL,
    iva DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) NOT NULL,
    uuid_cfdi VARCHAR(50),
    estado VARCHAR(30) DEFAULT 'EMITIDA', -- EMITIDA, APLICADA, CANCELADA
    asiento_contable_id UUID REFERENCES asientos_contables(id),
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE NOTAS DE CRÉDITO CLIENTES
CREATE TABLE notas_credito_cliente_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nota_id UUID NOT NULL REFERENCES notas_credito_cliente(id) ON DELETE CASCADE,
    factura_detalle_id UUID REFERENCES facturas_venta_detalle(id),
    producto_id UUID NOT NULL,
    cantidad DECIMAL(15,3) NOT NULL,
    precio_unitario DECIMAL(15,2) NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    motivo_especifico TEXT
);

-- COBROS A CLIENTES
CREATE TABLE cobros_cliente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    numero_cobro VARCHAR(30) NOT NULL,
    fecha_cobro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    monto DECIMAL(15,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'MXN',
    tipo_cambio DECIMAL(10,4) DEFAULT 1.0,
    metodo_pago VARCHAR(50) NOT NULL,
    referencia VARCHAR(100),
    banco_id UUID,
    cuenta_bancaria_id UUID,
    estado VARCHAR(30) DEFAULT 'APLICADO',
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- APLICACIÓN DE COBROS A FACTURAS
CREATE TABLE cobros_facturas_cliente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cobro_id UUID NOT NULL REFERENCES cobros_cliente(id) ON DELETE CASCADE,
    factura_id UUID NOT NULL REFERENCES facturas_venta(id),
    monto_aplicado DECIMAL(15,2) NOT NULL,
    fecha_aplicacion TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MÓDULO 5: INVENTARIO Y KARDEX
-- ============================================================================

-- PRODUCTOS
CREATE TABLE productos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sku VARCHAR(50) NOT NULL,
    codigo_barras VARCHAR(50),
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id UUID,
    marca_id UUID,
    tipo_producto VARCHAR(50) NOT NULL,
    unidad_medida VARCHAR(20) DEFAULT 'PIEZA',
    costo_estandar DECIMAL(15,2) DEFAULT 0,
    precio_venta DECIMAL(15,2) NOT NULL,
    precio_mayoreo DECIMAL(15,2),
    metodo_costeo VARCHAR(20) DEFAULT 'PROMEDIO', -- PEPS, PROMEDIO
    stock_minimo DECIMAL(15,3) DEFAULT 0,
    stock_maximo DECIMAL(15,3) DEFAULT 0,
    punto_reorden DECIMAL(15,3) DEFAULT 0,
    requiere_receta BOOLEAN DEFAULT FALSE,
    es_servicio BOOLEAN DEFAULT FALSE,
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, sku)
);

CREATE INDEX idx_productos_sku ON productos(empresa_id, sku);
CREATE INDEX idx_productos_barras ON productos(codigo_barras);

-- ALMACENES
CREATE TABLE almacenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(200),
    tipo VARCHAR(30) DEFAULT 'PRINCIPAL', -- PRINCIPAL, TRANSITO, DEVOLUCIONES
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, codigo)
);

-- INVENTARIO (Stock por producto y almacén)
CREATE TABLE inventario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    producto_id UUID NOT NULL REFERENCES productos(id),
    almacen_id UUID NOT NULL REFERENCES almacenes(id),
    stock_actual DECIMAL(15,3) DEFAULT 0,
    stock_comprometido DECIMAL(15,3) DEFAULT 0,
    stock_disponible DECIMAL(15,3) GENERATED ALWAYS AS (stock_actual - stock_comprometido) STORED,
    costo_promedio DECIMAL(15,2) DEFAULT 0,
    ultimo_costo DECIMAL(15,2) DEFAULT 0,
    fecha_ultimo_movimiento TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(producto_id, almacen_id)
);

CREATE INDEX idx_inventario_producto ON inventario(producto_id);
CREATE INDEX idx_inventario_almacen ON inventario(almacen_id);

-- KARDEX (Movimientos de inventario)
CREATE TABLE kardex (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    producto_id UUID NOT NULL REFERENCES productos(id),
    almacen_id UUID NOT NULL REFERENCES almacenes(id),
    fecha_movimiento TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tipo_movimiento VARCHAR(50) NOT NULL,
    -- Tipos: COMPRA, VENTA, DEVOLUCION_COMPRA, DEVOLUCION_VENTA, 
    --        TRANSFERENCIA_ENTRADA, TRANSFERENCIA_SALIDA, AJUSTE_POSITIVO, 
    --        AJUSTE_NEGATIVO, MERMA, PRODUCCION_ENTRADA, PRODUCCION_SALIDA
    
    referencia_tipo VARCHAR(50), -- COMPRA, VENTA, TRANSFERENCIA, AJUSTE
    referencia_id UUID,
    
    -- Entradas
    cantidad_entrada DECIMAL(15,3) DEFAULT 0,
    costo_unitario_entrada DECIMAL(15,2) DEFAULT 0,
    costo_total_entrada DECIMAL(15,2) DEFAULT 0,
    
    -- Salidas
    cantidad_salida DECIMAL(15,3) DEFAULT 0,
    costo_unitario_salida DECIMAL(15,2) DEFAULT 0,
    costo_total_salida DECIMAL(15,2) DEFAULT 0,
    
    -- Saldos
    stock_anterior DECIMAL(15,3) NOT NULL,
    costo_promedio_anterior DECIMAL(15,2) NOT NULL,
    stock_nuevo DECIMAL(15,3) NOT NULL,
    costo_promedio_nuevo DECIMAL(15,2) NOT NULL,
    
    -- Lote y caducidad
    lote VARCHAR(50),
    fecha_caducidad DATE,
    
    -- Auditoría
    motivo TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kardex_producto ON kardex(producto_id);
CREATE INDEX idx_kardex_almacen ON kardex(almacen_id);
CREATE INDEX idx_kardex_fecha ON kardex(fecha_movimiento);
CREATE INDEX idx_kardex_referencia ON kardex(referencia_tipo, referencia_id);

-- Función para calcular costo promedio
CREATE OR REPLACE FUNCTION fn_calcular_costo_promedio(
    p_producto_id UUID,
    p_almacen_id UUID
)
RETURNS DECIMAL AS $$
DECLARE
    v_costo_promedio DECIMAL(15,2);
BEGIN
    SELECT costo_promedio_nuevo
    INTO v_costo_promedio
    FROM kardex
    WHERE producto_id = p_producto_id
        AND almacen_id = p_almacen_id
    ORDER BY fecha_movimiento DESC
    LIMIT 1;
    
    RETURN COALESCE(v_costo_promedio, 0);
END;
$$ LANGUAGE plpgsql;

-- TRANSFERENCIAS ENTRE SUCURSALES
CREATE TABLE transferencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    numero_transferencia VARCHAR(30) NOT NULL,
    sucursal_origen_id UUID NOT NULL REFERENCES sucursales(id),
    sucursal_destino_id UUID NOT NULL REFERENCES sucursales(id),
    almacen_origen_id UUID NOT NULL REFERENCES almacenes(id),
    almacen_destino_id UUID NOT NULL REFERENCES almacenes(id),
    fecha_solicitud DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_envio TIMESTAMPTZ,
    fecha_recepcion TIMESTAMPTZ,
    estado VARCHAR(30) DEFAULT 'SOLICITADA', -- SOLICITADA, EN_TRANSITO, RECIBIDA, CANCELADA
    motivo TEXT,
    usuario_solicitante_id UUID REFERENCES usuarios(id),
    usuario_envio_id UUID REFERENCES usuarios(id),
    usuario_recepcion_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE TRANSFERENCIAS
CREATE TABLE transferencias_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transferencia_id UUID NOT NULL REFERENCES transferencias(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id),
    cantidad_solicitada DECIMAL(15,3) NOT NULL,
    cantidad_enviada DECIMAL(15,3) DEFAULT 0,
    cantidad_recibida DECIMAL(15,3) DEFAULT 0,
    costo_unitario DECIMAL(15,2),
    lote VARCHAR(50)
);

-- AJUSTES DE INVENTARIO
CREATE TABLE ajustes_inventario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    almacen_id UUID NOT NULL REFERENCES almacenes(id),
    numero_ajuste VARCHAR(30) NOT NULL,
    fecha_ajuste TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tipo_ajuste VARCHAR(30) NOT NULL, -- POSITIVO, NEGATIVO
    motivo TEXT NOT NULL,
    estado VARCHAR(30) DEFAULT 'APLICADO', -- BORRADOR, APLICADO, CANCELADO
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE AJUSTES
CREATE TABLE ajustes_inventario_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ajuste_id UUID NOT NULL REFERENCES ajustes_inventario(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id),
    cantidad_anterior DECIMAL(15,3) NOT NULL,
    cantidad_nueva DECIMAL(15,3) NOT NULL,
    diferencia DECIMAL(15,3) GENERATED ALWAYS AS (cantidad_nueva - cantidad_anterior) STORED,
    costo_unitario DECIMAL(15,2) NOT NULL,
    motivo_especifico TEXT
);

-- INVENTARIOS FÍSICOS
CREATE TABLE inventarios_fisicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    almacen_id UUID NOT NULL REFERENCES almacenes(id),
    numero_inventario VARCHAR(30) NOT NULL,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ,
    estado VARCHAR(30) DEFAULT 'EN_PROCESO', -- EN_PROCESO, COMPLETADO, CANCELADO
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE INVENTARIOS FÍSICOS
CREATE TABLE inventarios_fisicos_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventario_id UUID NOT NULL REFERENCES inventarios_fisicos(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id),
    stock_sistema DECIMAL(15,3) NOT NULL,
    stock_fisico DECIMAL(15,3) NOT NULL,
    diferencia DECIMAL(15,3) GENERATED ALWAYS AS (stock_fisico - stock_sistema) STORED,
    costo_unitario DECIMAL(15,2) NOT NULL,
    valor_diferencia DECIMAL(15,2) GENERATED ALWAYS AS (diferencia * costo_unitario) STORED,
    motivo_diferencia TEXT,
    contador_id UUID REFERENCES usuarios(id)
);

-- ============================================================================
-- MÓDULO 6: TESORERÍA Y BANCOS
-- ============================================================================

-- BANCOS
CREATE TABLE bancos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(20),
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CUENTAS BANCARIAS
CREATE TABLE cuentas_bancarias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    banco_id UUID NOT NULL REFERENCES bancos(id),
    numero_cuenta VARCHAR(50) NOT NULL,
    clabe VARCHAR(50),
    tipo_cuenta VARCHAR(30) NOT NULL, -- CHEQUES, AHORRO, TRANSFERENCIA
    moneda VARCHAR(3) DEFAULT 'MXN',
    saldo_inicial DECIMAL(15,2) DEFAULT 0,
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    esta_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, numero_cuenta)
);

-- MOVIMIENTOS BANCARIOS
CREATE TABLE movimientos_bancarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_bancaria_id UUID NOT NULL REFERENCES cuentas_bancarias(id),
    fecha_movimiento TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tipo_movimiento VARCHAR(30) NOT NULL, -- DEPOSITO, RETIRO, TRANSFERENCIA, CARGO, ABONO
    concepto VARCHAR(500) NOT NULL,
    referencia VARCHAR(100),
    monto DECIMAL(15,2) NOT NULL,
    saldo_despues DECIMAL(15,2),
    conciliado BOOLEAN DEFAULT FALSE,
    fecha_conciliacion TIMESTAMPTZ,
    referencia_tipo VARCHAR(50), -- PAGO, COBRO, TRANSFERENCIA
    referencia_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mov_bancarios_cuenta ON movimientos_bancarios(cuenta_bancaria_id);
CREATE INDEX idx_mov_bancarios_fecha ON movimientos_bancarios(fecha_movimiento);

-- CONCILIACIONES BANCARIAS
CREATE TABLE conciliaciones_bancarias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_bancaria_id UUID NOT NULL REFERENCES cuentas_bancarias(id),
    periodo DATE NOT NULL,
    fecha_conciliacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    saldo_libreta DECIMAL(15,2) NOT NULL,
    saldo_banco DECIMAL(15,2) NOT NULL,
    depositos_no_conciliados DECIMAL(15,2) DEFAULT 0,
    cargos_no_conciliados DECIMAL(15,2) DEFAULT 0,
    diferencia DECIMAL(15,2) GENERATED ALWAYS AS (saldo_libreta - saldo_banco) STORED,
    estado VARCHAR(30) DEFAULT 'CONCILIADO',
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CAJAS
CREATE TABLE cajas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    nombre VARCHAR(100) NOT NULL,
    numero_caja INTEGER NOT NULL,
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    esta_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sucursal_id, numero_caja)
);

-- CORTES DE CAJA
CREATE TABLE cortes_caja (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    caja_id UUID NOT NULL REFERENCES cajas(id),
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    fecha_apertura TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_cierre TIMESTAMPTZ,
    monto_inicial DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_ventas DECIMAL(15,2) DEFAULT 0,
    total_cobros DECIMAL(15,2) DEFAULT 0,
    total_retiros DECIMAL(15,2) DEFAULT 0,
    total_ingresos DECIMAL(15,2) DEFAULT 0,
    monto_esperado DECIMAL(15,2) GENERATED ALWAYS AS (
        monto_inicial + total_ventas + total_cobros + total_ingresos - total_retiros
    ) STORED,
    monto_real DECIMAL(15,2),
    diferencia DECIMAL(15,2) GENERATED ALWAYS AS (monto_real - monto_esperado) STORED,
    estado VARCHAR(30) DEFAULT 'ABIERTO',
    observaciones TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- MOVIMIENTOS DE CAJA
CREATE TABLE movimientos_caja (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    corte_caja_id UUID NOT NULL REFERENCES cortes_caja(id),
    tipo_movimiento VARCHAR(30) NOT NULL, -- VENTA, COBRO, RETIRO, INGRESO, AJUSTE
    concepto VARCHAR(500) NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    metodo_pago VARCHAR(50),
    referencia_tipo VARCHAR(50),
    referencia_id UUID,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MÓDULO 7: ACTIVOS FIJOS
-- ============================================================================

-- CATEGORÍAS DE ACTIVOS
CREATE TABLE categorias_activo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    nombre VARCHAR(100) NOT NULL,
    vida_util_anios INTEGER NOT NULL,
    metodo_depreciacion VARCHAR(30) DEFAULT 'LINEAL', -- LINEAL, SUMA_DIGITOS, UNIDADES
    cuenta_activo_id UUID REFERENCES cuentas_contables(id),
    cuenta_depreciacion_id UUID REFERENCES cuentas_contables(id),
    cuenta_gasto_id UUID REFERENCES cuentas_contables(id),
    esta_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ACTIVOS FIJOS
CREATE TABLE activos_fijos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    categoria_id UUID NOT NULL REFERENCES categorias_activo(id),
    codigo VARCHAR(30) NOT NULL,
    descripcion VARCHAR(300) NOT NULL,
    fecha_adquisicion DATE NOT NULL,
    costo_adquisicion DECIMAL(15,2) NOT NULL,
    valor_residual DECIMAL(15,2) DEFAULT 0,
    vida_util_meses INTEGER NOT NULL,
    fecha_inicio_depreciacion DATE NOT NULL,
    depreciacion_acumulada DECIMAL(15,2) DEFAULT 0,
    valor_neto DECIMAL(15,2) GENERATED ALWAYS AS (
        costo_adquisicion - depreciacion_acumulada
    ) STORED,
    estado VARCHAR(30) DEFAULT 'ACTIVO', -- ACTIVO, BAJA, VENDIDO, EN_REPARACION
    ubicacion VARCHAR(200),
    numero_serie VARCHAR(100),
    proveedor_id UUID REFERENCES proveedores(id),
    factura_id UUID REFERENCES facturas_proveedor(id),
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, codigo)
);

-- DEPRECIACIONES
CREATE TABLE depreciaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activo_id UUID NOT NULL REFERENCES activos_fijos(id),
    periodo DATE NOT NULL,
    depreciacion_mensual DECIMAL(15,2) NOT NULL,
    depreciacion_acumulada DECIMAL(15,2) NOT NULL,
    valor_neto DECIMAL(15,2) NOT NULL,
    asiento_contable_id UUID REFERENCES asientos_contables(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MÓDULO 8: NÓMINA
-- ============================================================================

-- EMPLEADOS
CREATE TABLE empleados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    sucursal_id UUID NOT NULL REFERENCES sucursales(id),
    numero_empleado VARCHAR(20) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    rfc VARCHAR(20) NOT NULL,
    curp VARCHAR(18) NOT NULL,
    nss VARCHAR(20),
    fecha_nacimiento DATE,
    fecha_ingreso DATE NOT NULL,
    puesto VARCHAR(100),
    departamento VARCHAR(100),
    salario_diario DECIMAL(15,2) NOT NULL,
    salario_integrado DECIMAL(15,2),
    periodicidad VARCHAR(20) DEFAULT 'QUINCENAL', -- SEMANAL, QUINCENAL, MENSUAL
    banco_id UUID REFERENCES bancos(id),
    cuenta_bancaria VARCHAR(50),
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    esta_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, numero_empleado)
);

-- PERCEPCIONES
CREATE TABLE percepciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(30) NOT NULL, -- SUELDO, HORAS_EXTRA, BONOS, COMISIONES, AGUINALDO, VACACIONES
    gravita BOOLEAN DEFAULT TRUE,
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    esta_activa BOOLEAN DEFAULT TRUE,
    UNIQUE(empresa_id, codigo)
);

-- DEDUCCIONES
CREATE TABLE deducciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(30) NOT NULL, -- IMSS, ISR, FONDO_AHORRO, PRESTAMO, PENSION_ALIMENTICIA
    cuenta_contable_id UUID REFERENCES cuentas_contables(id),
    esta_activa BOOLEAN DEFAULT TRUE,
    UNIQUE(empresa_id, codigo)
);

-- NOMINAS (Cabecera)
CREATE TABLE nominas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    fecha_pago DATE NOT NULL,
    total_percepciones DECIMAL(15,2) DEFAULT 0,
    total_deducciones DECIMAL(15,2) DEFAULT 0,
    total_neto DECIMAL(15,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'BORRADOR', -- BORRADOR, CALCULADA, TIMBRADA, PAGADA, CANCELADA
    uuid_timbrado VARCHAR(50),
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- DETALLE NOMINAS (Por empleado)
CREATE TABLE nominas_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nomina_id UUID NOT NULL REFERENCES nominas(id) ON DELETE CASCADE,
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    dias_trabajados DECIMAL(5,2) NOT NULL,
    salario_base DECIMAL(15,2) NOT NULL,
    total_percepciones DECIMAL(15,2) DEFAULT 0,
    total_deducciones DECIMAL(15,2) DEFAULT 0,
    total_neto DECIMAL(15,2) DEFAULT 0,
    asiento_contable_id UUID REFERENCES asientos_contables(id)
);

-- DETALLE PERCEPCIONES NOMINA
CREATE TABLE nomina_percepciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nomina_detalle_id UUID NOT NULL REFERENCES nominas_detalle(id) ON DELETE CASCADE,
    percepcion_id UUID NOT NULL REFERENCES percepciones(id),
    importe DECIMAL(15,2) NOT NULL
);

-- DETALLE DEDUCCIONES NOMINA
CREATE TABLE nomina_deducciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nomina_detalle_id UUID NOT NULL REFERENCES nominas_detalle(id) ON DELETE CASCADE,
    deduccion_id UUID NOT NULL REFERENCES deducciones(id),
    importe DECIMAL(15,2) NOT NULL
);

-- ============================================================================
-- MÓDULO 9: AUDITORÍA
-- ============================================================================

CREATE TABLE auditoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID,
    accion VARCHAR(50) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    entidad VARCHAR(50) NOT NULL,
    entidad_id UUID,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address INET,
    user_agent TEXT,
    creado_en TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX idx_auditoria_entidad ON auditoria(entidad, entidad_id);
CREATE INDEX idx_auditoria_fecha ON auditoria(creado_en);

-- ============================================================================
-- TRIGGERS DE AUDITORÍA
-- ============================================================================

CREATE TRIGGER tr_auditoria_productos
AFTER INSERT OR UPDATE OR DELETE ON productos
FOR EACH ROW EXECUTE FUNCTION fn_auditoria();

CREATE TRIGGER tr_auditoria_facturas_venta
AFTER INSERT OR UPDATE OR DELETE ON facturas_venta
FOR EACH ROW EXECUTE FUNCTION fn_auditoria();

CREATE TRIGGER tr_auditoria_facturas_proveedor
AFTER INSERT OR UPDATE OR DELETE ON facturas_proveedor
FOR EACH ROW EXECUTE FUNCTION fn_auditoria();

-- ============================================================================
-- FIN DEL ESQUEMA
-- ============================================================================