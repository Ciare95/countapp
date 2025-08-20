-- Tabla de roles
CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50)
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT REFERENCES rol(id)
);

-- Tabla de clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    documento VARCHAR(20) UNIQUE
);

-- Tabla de ventas
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    fecha_venta TIMESTAMP NOT NULL,
    total_venta NUMERIC(10,2),
    id_cliente INT REFERENCES clientes(id),
    id_usuarios INT,
    saldo NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente','cancelada'))
);

-- Tabla de categorías
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla de productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    id_categorias INT REFERENCES categorias(id),
    nombre VARCHAR(100),
    stock INT,
    precio NUMERIC(10,2) NOT NULL,
    precio_compra NUMERIC(10,2),
    es_servicio BOOLEAN DEFAULT FALSE
);

-- Tabla de detalle de ventas
CREATE TABLE detalle_ventas (
    id SERIAL PRIMARY KEY,
    id_usuarios INT,
    id_ventas INT REFERENCES ventas(id),
    id_productos INT REFERENCES productos(id),
    id_clientes INT REFERENCES clientes(id),
    cantidad INT
);

-- Tabla de abonos
CREATE TABLE abonos (
    id SERIAL PRIMARY KEY,
    id_venta INT REFERENCES ventas(id) NOT NULL,
    fecha_abono TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto NUMERIC(10,2) NOT NULL
);

-- Tabla de facturas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    fecha_factura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL,
    id_proveedor INT REFERENCES proveedores(id),
    numero_factura VARCHAR(255) NOT NULL
);

-- Tabla de facturas de fabricación
CREATE TABLE facturas_fabricacion (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(255) UNIQUE NOT NULL,
    id_proveedor INT REFERENCES proveedores(id) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL
);

-- Tabla de ingredientes
CREATE TABLE ingredientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Tabla de ingredientes en factura
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

-- Tabla de ingredientes por producto
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

-- Tabla de inventario de ingredientes
CREATE TABLE inventario_ingredientes (
    id SERIAL PRIMARY KEY,
    id_ingrediente INT REFERENCES ingredientes(id) NOT NULL,
    cantidad NUMERIC(10,2) DEFAULT 0.00,
    costo_promedio NUMERIC(10,2)
);

-- Tabla de negocios
CREATE TABLE negocios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(50) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(50) NOT NULL,
    email VARCHAR(255)
);

-- Tabla de otros egresos
CREATE TABLE otros_egresos (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL,
    valor NUMERIC(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos fabricados
CREATE TABLE productos_fabricados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida VARCHAR(20) CHECK (unidad_medida IN ('gramos','kilos','litros','mililitros','cc','galon','garrafa')) NOT NULL,
    costo_total NUMERIC(20,2),
    precio_venta NUMERIC(10,2) DEFAULT 0.00,
    cantidad_producida NUMERIC(10,2) NOT NULL
);

-- Tabla de productos en factura
CREATE TABLE productos_factura (
    id SERIAL PRIMARY KEY,
    id_factura INT REFERENCES facturas(id),
    id_producto INT REFERENCES productos(id),
    cantidad INT,
    precio_compra NUMERIC(10,2),
    precio_venta NUMERIC(10,2),
    porcentaje_iva NUMERIC(5,2)
);

-- Tabla de proveedores
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(255),
    telefono VARCHAR(15)
);

-- Tabla de backup de clientes (opcional)
CREATE TABLE clientes_backup (
    id SERIAL PRIMARY KEY,
    primer_nombre VARCHAR(45) NOT NULL,
    segundo_nombre VARCHAR(45),
    primer_apellido VARCHAR(45) NOT NULL,
    segundo_apellido VARCHAR(45)
);
