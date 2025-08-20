import psycopg2
from app.db import connection_pool

def check_existing_tables():
    """Verificar qué tablas existen realmente en la base de datos"""
    conn = None
    cursor = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Consultar todas las tablas en la base de datos
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("=== TABLAS EXISTENTES EN LA BASE DE DATOS ===")
        for table in tables:
            print(f"- {table[0]}")
        
        # Verificar específicamente la tabla productos
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'productos'
            )
        """)
        productos_exists = cursor.fetchone()[0]
        print(f"\n¿Existe la tabla 'productos'? {productos_exists}")
        
        # Si existe, mostrar su estructura
        if productos_exists:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'productos'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("\n=== ESTRUCTURA DE LA TABLA 'productos' ===")
            for column in columns:
                print(f"- {column[0]}: {column[1]} ({'NULL' if column[2] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"Error al verificar tablas: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)

def check_table_creation_logs():
    """Verificar si hay logs de creación de tablas"""
    conn = None
    cursor = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Verificar si existe alguna tabla de logs o información del sistema
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('schema_migrations', 'migrations', 'alembic_version')
            )
        """)
        has_migration_table = cursor.fetchone()[0]
        print(f"\n¿Existe tabla de migraciones? {has_migration_table}")
        
    except Exception as e:
        print(f"Error al verificar logs: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)

if __name__ == "__main__":
    print("Verificando estado de la base de datos...")
    check_existing_tables()
    check_table_creation_logs()
