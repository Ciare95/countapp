-- Tabla de roles
CREATE TABLE rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50)
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT,
    FOREIGN KEY (id_rol) REFERENCES rol(id)
);

-- Tabla de clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    documento VARCHAR(20) UNIQUE
);

-- Tabla de ventas
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_venta TIMESTAMP NOT NULL,
    total_venta FLOAT(10,2),
    id_cliente INT,
    id_usuarios INT,
    saldo FLOAT(10,2) NOT NULL DEFAULT 0.00,
    estado ENUM('pendiente', 'cancelada') DEFAULT 'pendiente',
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

-- Tabla de categorías
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla de productos
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_categorias INT,
    nombre VARCHAR(100),
    stock INT,
    precio FLOAT(10,2) NOT NULL,
    precio_compra DECIMAL(10,2),
    es_servicio TINYINT(1) DEFAULT 0,
    FOREIGN KEY (id_categorias) REFERENCES categorias(id)
);

-- Tabla de detalle de ventas
CREATE TABLE detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuarios INT,
    id_ventas INT,
    id_productos INT,
    id_clientes INT,
    cantidad INT,
    FOREIGN KEY (id_ventas) REFERENCES ventas(id),
    FOREIGN KEY (id_productos) REFERENCES productos(id)
);

-- Tabla de abonos
CREATE TABLE abonos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    fecha_abono TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto FLOAT(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id)
);

-- Tabla de facturas
CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_factura DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    id_proveedor INT,
    numero_factura VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
);

-- Tabla de facturas de fabricación
CREATE TABLE facturas_fabricacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_factura VARCHAR(255) UNIQUE NOT NULL,
    id_proveedor INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total FLOAT(10,2) NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
);

-- Tabla de ingredientes
CREATE TABLE ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Tabla de ingredientes en factura
CREATE TABLE ingredientes_factura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL,
    id_ingrediente INT NOT NULL,
    cantidad FLOAT(10,2) NOT NULL,
    precio_unitario FLOAT(10,2) NOT NULL,
    subtotal FLOAT(10,2) AS (cantidad * precio_unitario) STORED,
    medida_ingrediente VARCHAR(255),
    iva FLOAT(10,2),
    transporte FLOAT(10,2),
    costo_final FLOAT(10,2),
    FOREIGN KEY (id_factura) REFERENCES facturas_fabricacion(id),
    FOREIGN KEY (id_ingrediente) REFERENCES ingredientes(id)
);

-- Tabla de ingredientes por producto
CREATE TABLE ingredientes_producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    ingrediente_id INT NOT NULL,
    costo_factura DECIMAL(10,2) NOT NULL,
    costo_ing_por_producto DECIMAL(10,2) DEFAULT 0.00,
    unidad_medida ENUM('gramos','kilos','litros','mililitros','cc','galon','garrafa'),
    cantidad_ing DECIMAL(10,2),
    cantidad_factura ENUM('gramos','kilos','litros','mililitros','cc','galon','garrafa'),
    costo_empaque DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (producto_id) REFERENCES productos_fabricados(id),
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
);

-- Tabla de inventario de ingredientes
CREATE TABLE inventario_ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ingrediente INT NOT NULL,
    cantidad FLOAT(10,2) DEFAULT 0.00,
    costo_promedio FLOAT(10,2),
    FOREIGN KEY (id_ingrediente) REFERENCES ingredientes(id)
);

-- Tabla de negocios
CREATE TABLE negocios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(50) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(50) NOT NULL,
    email VARCHAR(255)
);

-- Tabla de otros egresos
CREATE TABLE otros_egresos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos fabricados
CREATE TABLE productos_fabricados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida ENUM('gramos','kilos','litros','mililitros','cc','galon','garrafa') NOT NULL,
    costo_total DECIMAL(20,2),
    precio_venta DECIMAL(10,2) DEFAULT 0.00,
    cantidad_producida DECIMAL(10,2) NOT NULL
);

-- Tabla de productos en factura
CREATE TABLE productos_factura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT,
    id_producto INT,
    cantidad INT,
    precio_compra DECIMAL(10,2),
    precio_venta DECIMAL(10,2),
    porcentaje_iva DECIMAL(5,2),
    FOREIGN KEY (id_factura) REFERENCES facturas(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);

-- Tabla de proveedores
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(255),
    telefono VARCHAR(15)
);

-- Tabla de backup de clientes (opcional)
CREATE TABLE clientes_backup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    primer_nombre VARCHAR(45) NOT NULL,
    segundo_nombre VARCHAR(45),
    primer_apellido VARCHAR(45) NOT NULL,
    segundo_apellido VARCHAR(45)
);
