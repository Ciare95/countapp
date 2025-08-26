#!/usr/bin/env python3
"""
Script para probar el funcionamiento del pool de conexiones
y detectar posibles fugas de conexiones.
"""

import time
from app.db import connection_pool
from app.db_utils import get_db_cursor

def test_connection_pool():
    """Prueba el pool de conexiones con múltiples operaciones"""
    print("=== Iniciando prueba del pool de conexiones ===")
    
    # Prueba 1: Obtener y liberar conexiones básicas
    print("\n1. Probando obtención y liberación básica de conexiones...")
    connections = []
    for i in range(5):
        try:
            conn = connection_pool.getconn()
            connections.append(conn)
            print(f"   Conexión {i+1} obtenida exitosamente")
        except Exception as e:
            print(f"   Error al obtener conexión {i+1}: {e}")
    
    # Liberar todas las conexiones
    for i, conn in enumerate(connections):
        try:
            connection_pool.putconn(conn)
            print(f"   Conexión {i+1} liberada exitosamente")
        except Exception as e:
            print(f"   Error al liberar conexión {i+1}: {e}")
    
    # Prueba 2: Usar el context manager
    print("\n2. Probando context manager...")
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"   Versión de PostgreSQL: {version[0]}")
        print("   Context manager funcionó correctamente")
    except Exception as e:
        print(f"   Error con context manager: {e}")
    
    # Prueba 3: Ejecutar múltiples consultas
    print("\n3. Probando múltiples consultas...")
    queries = [
        "SELECT COUNT(*) FROM usuarios",
        "SELECT COUNT(*) FROM productos", 
        "SELECT COUNT(*) FROM categorias"
    ]
    
    for i, query in enumerate(queries):
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                print(f"   Consulta {i+1}: {result[0]} registros")
        except Exception as e:
            print(f"   Error en consulta {i+1}: {e}")
    
    # Prueba 4: Verificar estado del pool
    print("\n4. Verificando estado del pool...")
    try:
        # Intentar obtener más conexiones de las disponibles
        test_connections = []
        for i in range(35):  # Más que el máximo configurado (30)
            try:
                conn = connection_pool.getconn(timeout=2)
                test_connections.append(conn)
                print(f"   Conexión de prueba {i+1} obtenida")
            except Exception as e:
                print(f"   No se pudo obtener conexión {i+1}: {e}")
                break
        
        # Liberar todas las conexiones de prueba
        for conn in test_connections:
            try:
                connection_pool.putconn(conn)
            except:
                pass
                
    except Exception as e:
        print(f"   Error en prueba de estrés: {e}")
    
    print("\n=== Prueba completada ===")

if __name__ == "__main__":
    test_connection_pool()
