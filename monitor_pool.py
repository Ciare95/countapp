#!/usr/bin/env python3
"""
Script para monitorear el estado del pool de conexiones en tiempo real.
"""

import time
import psycopg2
from psycopg2 import pool
from app.db import connection_pool

def monitor_pool_status():
    """Monitorea y muestra el estado del pool de conexiones"""
    print("=== Monitor de Pool de Conexiones ===")
    print("Presiona Ctrl+C para detener el monitoreo\n")
    
    try:
        while True:
            # Intentar obtener información del pool (si es posible)
            pool_info = {}
            
            # Para SimpleConnectionPool, no hay métodos nativos para obtener stats
            # pero podemos intentar algunas pruebas
            
            # Prueba 1: Intentar obtener una conexión con timeout corto
            test_conn = None
            try:
                test_conn = connection_pool.getconn(timeout=1)
                pool_info['available'] = "Conexiones disponibles"
                connection_pool.putconn(test_conn)
            except pool.PoolError as e:
                if "connection pool exhausted" in str(e):
                    pool_info['status'] = "POOL AGOTADO"
                else:
                    pool_info['status'] = f"Error: {e}"
            except Exception as e:
                pool_info['status'] = f"Error general: {e}"
            
            # Prueba 2: Verificar conexiones activas en la base de datos
            try:
                with connection_pool.getconn() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT count(*) 
                            FROM pg_stat_activity 
                            WHERE datname = current_database()
                            AND state = 'active'
                        """)
                        active_connections = cursor.fetchone()[0]
                        pool_info['db_active'] = active_connections
            except Exception as e:
                pool_info['db_active_error'] = str(e)
            
            # Mostrar información
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Estado del pool:")
            for key, value in pool_info.items():
                print(f"  {key}: {value}")
            print("-" * 40)
            
            time.sleep(5)  # Esperar 5 segundos entre checks
            
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")
    except Exception as e:
        print(f"Error en el monitoreo: {e}")

def check_pool_health():
    """Realiza una verificación de salud del pool"""
    print("=== Verificación de Salud del Pool ===")
    
    checks = []
    
    # Check 1: ¿Se puede obtener una conexión?
    try:
        conn = connection_pool.getconn(timeout=5)
        checks.append(("Obtención de conexión", "✓ OK"))
        connection_pool.putconn(conn)
    except Exception as e:
        checks.append(("Obtención de conexión", f"✗ ERROR: {e}"))
    
    # Check 2: ¿Se puede ejecutar una consulta simple?
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    checks.append(("Consulta simple", "✓ OK"))
                else:
                    checks.append(("Consulta simple", "✗ RESULTADO INESPERADO"))
    except Exception as e:
        checks.append(("Consulta simple", f"✗ ERROR: {e}"))
    
    # Check 3: Verificar conexiones de base de datos
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        count(*) as total,
                        count(*) FILTER (WHERE state = 'active') as active,
                        count(*) FILTER (WHERE state = 'idle') as idle
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                stats = cursor.fetchone()
                checks.append(("Estadísticas DB", f"Total: {stats[0]}, Activas: {stats[1]}, Inactivas: {stats[2]}"))
    except Exception as e:
        checks.append(("Estadísticas DB", f"✗ ERROR: {e}"))
    
    # Mostrar resultados
    for check, result in checks:
        print(f"{check}: {result}")
    
    return all("✓" in result or "OK" in result for check, result in checks)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_pool_status()
    else:
        healthy = check_pool_health()
        if healthy:
            print("\n✓ El pool parece estar saludable")
        else:
            print("\n✗ El pool tiene problemas que requieren atención")
