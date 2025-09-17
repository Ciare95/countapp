#!/usr/bin/env python3
"""
Script para migrar la base de datos existente al esquema multi-negocio
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

def migrate_database():
    """Migrar la base de datos al esquema multi-negocio"""
    conn = create_connection()
    cursor = conn.cursor()
    
    print("Iniciando migración a esquema multi-negocio...")
    
    try:
        # 1. Crear un negocio por defecto con los datos existentes
        print("Creando negocio por defecto...")
        cursor.execute("""
            INSERT INTO negocios (nombre, nit, direccion, telefono, email)
            VALUES ('Mi Negocio', '000000000', 'Dirección por defecto', '0000000000', 'negocio@ejemplo.com')
            RETURNING id
        """)
        negocio_id = cursor.fetchone()[0]
        print(f"Negocio creado con ID: {negocio_id}")
        
        # 2. Actualizar usuarios existentes con el negocio por defecto
        print("Actualizando usuarios existentes...")
        cursor.execute("UPDATE usuarios SET id_negocio = %s WHERE id_negocio IS NULL", (negocio_id,))
        print(f"Usuarios actualizados: {cursor.rowcount}")
        
        # 3. Actualizar otras tablas con el campo id_negocio
        tables_to_migrate = [
            'clientes', 'categorias', 'productos', 'ventas', 'proveedores',
            'facturas', 'facturas_fabricacion', 'ingredientes', 'productos_fabricados',
            'otros_egresos'
        ]
        
        for table in tables_to_migrate:
            try:
                # Verificar si la tabla existe
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                if cursor.fetchone()[0]:
                    # Actualizar registros existentes con el negocio por defecto
                    cursor.execute(f"UPDATE {table} SET id_negocio = %s WHERE id_negocio IS NULL", (negocio_id,))
                    print(f"Registros actualizados en {table}: {cursor.rowcount}")
            except Exception as e:
                print(f"Error procesando tabla {table}: {e}")
                conn.rollback()
                continue
        
        # 4. Crear índices para mejorar rendimiento (solo si las columnas existen)
        print("Creando índices...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_usuarios_negocio ON usuarios(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_clientes_negocio ON clientes(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_productos_negocio ON productos(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_categorias_negocio ON categorias(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_negocio ON ventas(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_proveedores_negocio ON proveedores(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_facturas_negocio ON facturas(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_ingredientes_negocio ON ingredientes(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_productos_fabricados_negocio ON productos_fabricados(id_negocio)",
            "CREATE INDEX IF NOT EXISTS idx_otros_egresos_negocio ON otros_egresos(id_negocio)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"⚠️  No se pudo crear índice (puede que la columna no exista aún): {e}")
        
        # 5. Crear usuario superadmin si no existe
        print("Creando usuario superadmin...")
        cursor.execute("SELECT id FROM rol WHERE nombre = 'superadmin'")
        superadmin_role = cursor.fetchone()
        
        if not superadmin_role:
            cursor.execute("INSERT INTO rol (nombre) VALUES ('superadmin') RETURNING id")
            superadmin_role_id = cursor.fetchone()[0]
        else:
            superadmin_role_id = superadmin_role[0]
        
        # Verificar si ya existe un usuario superadmin
        cursor.execute("SELECT id FROM usuarios WHERE nombre = 'superadmin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO usuarios (nombre, contrasena, id_rol, id_negocio)
                VALUES ('superadmin', 'admin123', %s, NULL)
            """, (superadmin_role_id,))
            print("Usuario superadmin creado (superadmin/admin123)")
        else:
            print("Usuario superadmin ya existe")
        
        conn.commit()
        print("✅ Migración completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=== MIGRACIÓN A ESQUEMA MULTI-NEGOCIO ===")
    migrate_database()
