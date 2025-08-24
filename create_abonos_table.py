import os
import psycopg2
from psycopg2 import pool

# Database connection parameters
db_params = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_DATABASE", "sistema_papeleria"),
    "port": int(os.environ.get("DB_PORT", 5432)),
}

# Create a connection string
conn_string = f"host={db_params['host']} user={db_params['user']} password={db_params['password']} dbname={db_params['database']} port={db_params['port']} client_encoding=utf8"

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, conn_string)

def create_abonos_table():
    """
    Connects to the PostgreSQL database and creates the 'abonos' table if it doesn't exist.
    """
    connection = None
    try:
        # Get a connection from the pool
        connection = connection_pool.getconn()
        cursor = connection.cursor()

        # Check if the 'abonos' table exists
        cursor.execute("SELECT to_regclass('public.abonos');")
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("The 'abonos' table already exists.")
        else:
            # Create the 'abonos' table
            cursor.execute("""
                CREATE TABLE abonos (
                    id SERIAL PRIMARY KEY,
                    id_venta INT REFERENCES ventas(id) NOT NULL,
                    fecha_abono TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    monto NUMERIC(10,2) NOT NULL
                );
            """)
            connection.commit()
            print("The 'abonos' table was created successfully.")

    except psycopg2.Error as e:
        print(f"Error connecting to the database or creating the table: {e}")

    finally:
        if connection:
            # Return the connection to the pool
            connection_pool.putconn(connection)

if __name__ == '__main__':
    create_abonos_table()
