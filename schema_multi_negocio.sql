-- =============================================
-- ESQUEMA MULTI-NEGOCIO PARA APLICACIÓN SaaS
-- =============================================

-- Tabla de roles
CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50)
);

-- Tabla de negocios (ya existe, mantener estructura)
CREATE TABLE negocios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(50) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de usuarios con relación a negocio
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT REFERENCES rol(id),
    id_negocio INT REFERENCES negocios(id),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nombre, id_negocio) -- Usuario único por negocio
);

-- Tabla de clientes con relación a negocio
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    documento VARCHAR(20),
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(documento, id_negocio) -- Documento único por negocio
);

-- Tabla de categorías con relación a negocio
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(nombre, id_negocio) -- Categoría única por negocio
);

-- Tabla de productos con relación a negocio
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    id_categorias INT REFERENCES categorias(id),
    nombre VARCHAR(100),
    stock INT,
    precio NUMERIC(10,2) NOT NULL,
    precio_compra NUMERIC(10,2),
    es_servicio BOOLEAN DEFAULT FALSE,
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(nombre, id_negocio) -- Producto único por negocio
);

-- Tabla de ventas con relación a negocio
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    fecha_venta TIMESTAMP NOT NULL,
    total_venta NUMERIC(10,2),
    id_cliente INT REFERENCES clientes(id),
    id_usuarios INT REFERENCES usuarios(id),
    saldo NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente','cancelada')),
    id_negocio INT REFERENCES negocios(id)
);

-- Tabla de detalle de ventas (mantiene relación con venta que ya tiene negocio)
CREATE TABLE detalle_ventas (
    id SERIAL PRIMARY KEY,
    id_usuarios INT REFERENCES usuarios(id),
    id_ventas INT REFERENCES ventas(id),
    id_productos INT REFERENCES productos(id),
    id_clientes INT REFERENCES clientes(id),
    cantidad INT
);

-- Tabla de abonos (mantiene relación con venta que ya tiene negocio)
CREATE TABLE abonos (
    id SERIAL PRIMARY KEY,
    id_venta INT REFERENCES ventas(id) NOT NULL,
    fecha_abono TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto NUMERIC(10,2) NOT NULL
);

-- Tabla de proveedores con relación a negocio
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(255),
    telefono VARCHAR(15),
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(nit, id_negocio) -- NIT único por negocio
);

-- Tabla de facturas con relación a negocio
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    fecha_factura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL,
    id_proveedor INT REFERENCES proveedores(id),
    numero_factura VARCHAR(255) NOT NULL,
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(numero_factura, id_negocio) -- Factura única por negocio
);

-- Tabla de facturas de fabricación con relación a negocio
CREATE TABLE facturas_fabricacion (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(255) NOT NULL,
    id_proveedor INT REFERENCES proveedores(id) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL,
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(numero_factura, id_negocio) -- Factura fabricación única por negocio
);

-- Tabla de ingredientes con relación a negocio
CREATE TABLE ingredientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(nombre, id_negocio) -- Ingrediente único por negocio
);

-- Tabla de ingredientes en factura (mantiene relación con factura que ya tiene negocio)
CREATE TABLE ingredientes_factura (
    id SERIAL PRIMARY KEY,
    id_factura INT REFERENCES facturas_fabricacion(id) NOT NULL,
    id_ingrediente INT REFERENCES ingredientes(id) NOT NULL,
    cantidad NUMERIC(10,2) NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    medida_ingrediente VARCHAR(255),
    iva NUMERIC(10,2),
    transporte NUMERIC(10,2),
    costo_final NUMERIC(10,2)
);

-- Tabla de productos fabricados con relación a negocio
CREATE TABLE productos_fabricados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida VARCHAR(20) CHECK (unidad_medida IN ('gramos','kilos','litros','mililitros','cc','galon','garrafa')) NOT NULL,
    costo_total NUMERIC(20,2),
    precio_venta NUMERIC(10,2) DEFAULT 0.00,
    cantidad_producida NUMERIC(10,2) NOT NULL,
    id_negocio INT REFERENCES negocios(id),
    UNIQUE(nombre, id_negocio) -- Producto fabricado único por negocio
);

-- Tabla de ingredientes por producto (mantiene relación con productos fabricados que ya tienen negocio)
CREATE TABLE ingredientes_producto (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos_fabricados(id) NOT NULL,
    ingrediente_id INT REFERENCES ingredientes(id) NOT NULL,
    costo_factura NUMERIC(10,2) NOT NULL,
    costo_ing_por_producto NUMERIC(10,2) DEFAULT 0.00,
    unidad_medida VARCHAR(20) CHECK (unidad_medida IN ('gramos','kilos','litros','mililitros','cc','galon','garrafa')),
    cantidad_ing NUMERIC(10,2),
    cantidad_factura VARCHAR(20) CHECK (cantidad_factura IN ('gramos','kilos','litros','mililitros','cc','galon','garrafa')),
    costo_empaque NUMERIC(10,2) DEFAULT 0.00
);

-- Tabla de inventario de ingredientes (mantiene relación con ingredientes que ya tienen negocio)
CREATE TABLE inventario_ingredientes (
    id SERIAL PRIMARY KEY,
    id_ingrediente INT REFERENCES ingredientes(id) NOT NULL,
    cantidad NUMERIC(10,2) DEFAULT 0.00,
    costo_promedio NUMERIC(10,2)
);

-- Tabla de otros egresos con relación a negocio
CREATE TABLE otros_egresos (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL,
    valor NUMERIC(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_negocio INT REFERENCES negocios(id)
);

-- Tabla de productos en factura (mantiene relación con factura y productos que ya tienen negocio)
CREATE TABLE productos_factura (
    id SERIAL PRIMARY KEY,
    id_factura INT REFERENCES facturas(id),
    id_producto INT REFERENCES productos(id),
    cantidad INT,
    precio_compra NUMERIC(10,2),
    precio_venta NUMERIC(10,2),
    porcentaje_iva NUMERIC(5,2)
);

-- Tabla de planes de suscripción
CREATE TABLE planes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio_mensual NUMERIC(10,2) NOT NULL,
    max_usuarios INT NOT NULL,
    max_productos INT NOT NULL,
    max_clientes INT NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de suscripciones de negocios
CREATE TABLE suscripciones (
    id SERIAL PRIMARY KEY,
    id_negocio INT REFERENCES negocios(id) UNIQUE,
    id_plan INT REFERENCES planes(id),
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    metodo_pago VARCHAR(50),
    ultimo_pago TIMESTAMP
);

-- Insertar planes por defecto
INSERT INTO planes (nombre, precio_mensual, max_usuarios, max_productos, max_clientes) VALUES
('Básico', 29.99, 2, 100, 500),
('Profesional', 79.99, 5, 1000, 5000),
('Empresa', 199.99, 20, 10000, 50000);

-- Insertar roles por defecto
INSERT INTO rol (nombre) VALUES
('superadmin'),
('administrador'),
('usuario');

-- Crear índice para mejorar rendimiento en búsquedas por negocio
CREATE INDEX idx_usuarios_negocio ON usuarios(id_negocio);
CREATE INDEX idx_clientes_negocio ON clientes(id_negocio);
CREATE INDEX idx_productos_negocio ON productos(id_negocio);
CREATE INDEX idx_categorias_negocio ON categorias(id_negocio);
CREATE INDEX idx_ventas_negocio ON ventas(id_negocio);
CREATE INDEX idx_proveedores_negocio ON proveedores(id_negocio);
CREATE INDEX idx_facturas_negocio ON facturas(id_negocio);
CREATE INDEX idx_ingredientes_negocio ON ingredientes(id_negocio);
CREATE INDEX idx_productos_fabricados_negocio ON productos_fabricados(id_negocio);
CREATE INDEX idx_otros_egresos_negocio ON otros_egresos(id_negocio);
