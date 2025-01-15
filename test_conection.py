# test_connection.py
from app.db import connection_pool

def test():
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()
        print(f"Conexión exitosa. Hora del servidor: {result[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    test()