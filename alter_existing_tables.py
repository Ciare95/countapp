#!/usr/bin/env python3
"""
Script para alterar las tablas existentes agregando id_negocio
"""

import psycopg2
import os
from urllib.parse import urlparse
import sys

# Cargar variables de entorno desde .env si existe
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def get_db_config():
    """Obtener configuración de base de datos"""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if "render.com" in database_url and "sslmode" not in database_url:
            database_url += "?sslmode=require"
        result = urlparse(database_url)
        return {
            "user": result.username,
            "password": result.password,
            "host": result.hostname,
            "database": result.path[1:],
            "port": result.port,
        }
    else:
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "user": os.environ.get("DB_USER", "postgres"),
            "password": os.environ.get("DB_PASSWORD", ""),
            "database": os.environ.get("DB_DATABASE", "sistema_papeleria"),
            "port": int(os.environ.get("DB_PORT", 5432)),
        }

def create_connection():
    """Crear conexión a la base de datos"""
    dbconfig = get_db_config()
    try:
        # Usar string de conexión en lugar de parámetros individuales
        conn_string = f"host={dbconfig['host']} user={dbconfig['user']} password={dbconfig['password']} dbname={dbconfig['database']} port={dbconfig['port']}"
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        # Mostrar información de configuración para debugging
        print(f"Configuración usada: host={dbconfig['host']}, user={dbconfig['user']}, database={dbconfig['database']}, port={dbconfig['port']}")
        sys.exit(1)

def alter_tables():
    """Agregar columnas id_negocio a las tablas existentes"""
    conn = create_connection()
    cursor = conn.cursor()
    
    print("Agregando columnas id_negocio a tablas existentes...")
    
    try:
        # 1. Primero crear la tabla de planes si no existe
        print("Creando tabla de planes si no existe...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio_mensual NUMERIC(10,2) NOT NULL,
                max_usuarios INT NOT NULL,
                max_productos INT NOT NULL,
                max_clientes INT NOT NULL,
                activo BOOLEAN DEFAULT TRUE
            )
        """)
        
        # 2. Crear tabla de suscripciones si no existe
        print("Creando tabla de suscripciones si no existe...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suscripciones (
                id SERIAL PRIMARY KEY,
                id_negocio INTEGER,
                id_plan INTEGER,
                fecha_inicio TIMESTAMP NOT NULL,
                fecha_fin TIMESTAMP NOT NULL,
                activa BOOLEAN DEFAULT TRUE,
                metodo_pago VARCHAR(50),
                ultimo_pago TIMESTAMP,
                FOREIGN KEY (id_negocio) REFERENCES negocios(id),
                FOREIGN KEY (id_plan) REFERENCES planes(id)
            )
        """)
        
        # 3. Lista de tablas a las que agregar id_negocio
        tables_to_alter = [
            'usuarios', 'clientes', 'categorias', 'productos', 'ventas',
            'proveedores', 'facturas', 'facturas_fabricacion', 'ingredientes',
            'productos_fabricados', 'otros_egresos'
        ]
        
        for table in tables_to_alter:
            try:
                # Verificar si la tabla existe
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}')")
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Verificar si la columna id_negocio ya existe
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='{table}' AND column_name='id_negocio'
                    """)
                    column_exists = cursor.fetchone()
                    
                    if not column_exists:
                        print(f"Agregando columna id_negocio a tabla {table}...")
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN id_negocio INTEGER REFERENCES negocios(id)")
                        print(f"✅ Columna id_negocio agregada a {table}")
                    else:
                        print(f"✅ Columna id_negocio ya existe en {table}")
                else:
                    print(f"⚠️  Tabla {table} no existe, omitiendo...")
                    
            except Exception as e:
                print(f"❌ Error procesando tabla {table}: {e}")
                conn.rollback()
                continue
        
        # 4. Insertar planes por defecto si no existen
        print("Insertando planes por defecto...")
        cursor.execute("SELECT COUNT(*) FROM planes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO planes (nombre, precio_mensual, max_usuarios, max_productos, max_clientes) VALUES
                ('Básico', 29.99, 2, 100, 500),
                ('Profesional', 79.99, 5, 1000, 5000),
                ('Empresa', 199.99, 20, 10000, 50000)
            """)
            print("✅ Planes por defecto insertados")
        
        # 5. Insertar rol superadmin si no existe
        print("Insertando rol superadmin si no existe...")
        cursor.execute("SELECT id FROM rol WHERE nombre = 'superadmin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO rol (nombre) VALUES ('superadmin') RETURNING id")
            superadmin_role_id = cursor.fetchone()[0]
            print("✅ Rol superadmin creado")
        else:
            print("✅ Rol superadmin ya existe")
        
        conn.commit()
        print("✅ Alteración de tablas completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la alteración de tablas: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=== ALTERACIÓN DE TABLAS EXISTENTES ===")
    alter_tables()
