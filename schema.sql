CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INTEGER NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES rol(id)
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    documento VARCHAR(20) UNIQUE
);

CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    fecha_venta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    saldo DECIMAL(10,2) DEFAULT 0,
    id_cliente INTEGER NOT NULL,
    id_usuarios INTEGER NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_usuarios) REFERENCES usuarios(id)
);

CREATE TABLE detalle_ventas (
    id SERIAL PRIMARY KEY,
    id_ventas INTEGER NOT NULL,
    id_productos INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    FOREIGN KEY (id_ventas) REFERENCES ventas(id)
);
