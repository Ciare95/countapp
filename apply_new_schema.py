#!/usr/bin/env python3
"""
Script para aplicar el nuevo esquema multi-negocio a la base de datos
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

def apply_schema():
    """Aplicar el nuevo esquema multi-negocio"""
    conn = create_connection()
    cursor = conn.cursor()
    
    print("Aplicando nuevo esquema multi-negocio...")
    
    try:
        # Leer el archivo de esquema
        with open('schema_multi_negocio.sql', 'r') as f:
            schema_sql = f.read()
        
        # Dividir en sentencias individuales
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        # Ejecutar cada sentencia
        for i, stmt in enumerate(statements, 1):
            try:
                if stmt:  # Ignorar líneas vacías
                    print(f"Ejecutando sentencia {i}/{len(statements)}...")
                    cursor.execute(stmt)
            except Exception as e:
                print(f"Error ejecutando sentencia {i}: {e}")
                print(f"Sentencia: {stmt[:100]}...")  # Mostrar parte de la sentencia
                # Continuar con las siguientes sentencias
                conn.rollback()
                continue
        
        conn.commit()
        print("Esquema aplicado exitosamente!")
        
    except Exception as e:
        print(f"Error durante la aplicación del esquema: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=== APLICACIÓN DE ESQUEMA MULTI-NEGOCIO ===")
    apply_schema()
