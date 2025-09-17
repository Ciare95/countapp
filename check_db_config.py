#!/usr/bin/env python3
"""
Script para verificar la configuración de la base de datos
"""

import os
from urllib.parse import urlparse

def check_config():
    """Verificar la configuración de la base de datos"""
    print("=== VERIFICACIÓN DE CONFIGURACIÓN DE BASE DE DATOS ===")
    
    # Verificar DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        print(f"DATABASE_URL encontrado: {database_url}")
        result = urlparse(database_url)
        print(f"  - Host: {result.hostname}")
        print(f"  - Puerto: {result.port}")
        print(f"  - Base de datos: {result.path[1:]}")
        print(f"  - Usuario: {result.username}")
    else:
        print("DATABASE_URL no encontrado en variables de entorno")
    
    # Verificar variables individuales
    print("\nVariables de entorno individuales:")
    env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_DATABASE', 'DB_PORT']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  - {var}: {value}")
        else:
            print(f"  - {var}: NO CONFIGURADA")
    
    # Mostrar configuración final que se usaría
    print("\nConfiguración que se usaría:")
    if database_url:
        if "render.com" in database_url and "sslmode" not in database_url:
            database_url += "?sslmode=require"
        result = urlparse(database_url)
        dbconfig = {
            "user": result.username,
            "password": result.password,
            "host": result.hostname,
            "database": result.path[1:],
            "port": result.port,
        }
    else:
        dbconfig = {
            "host": os.environ.get("DB_HOST", "localhost"),
            "user": os.environ.get("DB_USER", "postgres"),
            "password": os.environ.get("DB_PASSWORD", ""),
            "database": os.environ.get("DB_DATABASE", "sistema_papeleria"),
            "port": int(os.environ.get("DB_PORT", 5432)),
        }
    
    print(f"  - Host: {dbconfig['host']}")
    print(f"  - Puerto: {dbconfig['port']}")
    print(f"  - Base de datos: {dbconfig['database']}")
    print(f"  - Usuario: {dbconfig['user']}")
    print(f"  - Password: {'***' if dbconfig['password'] else 'NO CONFIGURADO'}")

if __name__ == "__main__":
    check_config()
