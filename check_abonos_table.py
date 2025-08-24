import os
import psycopg2

def get_connection():
    # Connect exclusively via environment variables to avoid URL-encoding issues
    host = os.environ.get("DB_HOST", "localhost")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    database = os.environ.get("DB_DATABASE", "sistema_papeleria")
    port = int(os.environ.get("DB_PORT", 5432))
    return psycopg2.connect(host=host, user=user, password=password, dbname=database, port=port)

def main():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'abonos'
            )
        """)
        exists = cur.fetchone()[0]
        print(f"abonos_exists={exists}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
