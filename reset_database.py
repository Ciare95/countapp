import os
import psycopg2
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reset_database():
    """
    Connects to the database, drops all existing tables,
    and re-creates them using the schema_postgres.sql file.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logging.error("La variable de entorno DATABASE_URL no está configurada.")
        logging.error("Por favor, configúrala con la URL de tu base de datos de Render.")
        return

    conn = None
    cursor = None
    try:
        logging.info("Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        logging.info("Leyendo el archivo schema_postgres.sql...")
        with open('schema_postgres.sql', 'r') as f:
            schema_sql = f.read()

        # Lista de tablas a eliminar en el orden correcto para evitar problemas de FK
        tables_to_drop = [
            'detalle_ventas', 'abonos', 'productos_factura', 'ingredientes_factura',
            'ingredientes_producto', 'inventario_ingredientes', 'ventas', 'productos',
            'categorias', 'clientes', 'usuarios', 'rol', 'facturas', 'proveedores',
            'facturas_fabricacion', 'ingredientes', 'productos_fabricados',
            'negocios', 'otros_egresos', 'clientes_backup'
        ]

        logging.warning("Eliminando tablas existentes...")
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                logging.info(f"Tabla '{table}' eliminada exitosamente.")
            except psycopg2.errors.UndefinedTable:
                logging.warning(f"La tabla '{table}' no existe, se omite.")
                conn.rollback() # Anular la transacción fallida
            except Exception as e:
                logging.error(f"No se pudo eliminar la tabla '{table}': {e}")
                conn.rollback()


        logging.info("Ejecutando el script schema_postgres.sql para crear las nuevas tablas...")
        cursor.execute(schema_sql)
        conn.commit()
        logging.info("¡Base de datos reseteada y creada exitosamente con el nuevo esquema!")

    except Exception as e:
        logging.error(f"Ocurrió un error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logging.info("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    reset_database()
