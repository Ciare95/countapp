import psycopg2
from psycopg2 import pool
import sys
import logging
import traceback
import os

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

dbconfig = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_DATABASE", "sistema_papeleria"),
    "port": int(os.environ.get("DB_PORT", 5432)),
}

def test_basic_connection():
    try:
        logger.debug("Intentando conexión básica sin pool (Postgres)...")
        conn = psycopg2.connect(
            host=dbconfig['host'],
            user=dbconfig['user'],
            password=dbconfig['password'],
            database=dbconfig['database'],
            port=dbconfig['port']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        logger.debug(f"Versión del servidor Postgres: {version}")
        cursor.close()
        conn.close()
        return True
    except Exception:
        logger.error("Error en conexión básica:")
        logger.error(traceback.format_exc())
        return False

def create_pool():
    try:
        if not test_basic_connection():
            raise Exception("La conexión básica falló, no se intentará crear el pool")

        logger.debug("Intentando crear pool de conexiones (Postgres)...")

        connection_pool = pool.SimpleConnectionPool(
            1,                    # minconn
            15,                   # maxconn
            host=dbconfig['host'],
            user=dbconfig['user'],
            password=dbconfig['password'],
            database=dbconfig['database'],
            port=dbconfig['port']
        )

        logger.info("Pool de conexiones creado exitosamente")

        # Probar obtener una conexión del pool
        test_conn = connection_pool.getconn()
        connection_pool.putconn(test_conn)
        logger.debug("Prueba de conexión del pool exitosa")

        return connection_pool

    except Exception as e:
        logger.error("Error al crear pool:")
        logger.error(traceback.format_exc())
        raise

def ensure_roles_exist(pool):
    """Crea los roles 'administrador' y 'usuario' en tabla rol si no existen."""
    try:
        conn = pool.getconn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM rol WHERE nombre = 'administrador'")
        admin_exists = cursor.fetchone()[0] > 0

        cursor.execute("SELECT COUNT(*) FROM rol WHERE nombre = 'usuario'")
        user_exists = cursor.fetchone()[0] > 0

        if not admin_exists:
            cursor.execute("INSERT INTO rol (nombre) VALUES ('administrador')")
            logger.info("Rol 'administrador' creado exitosamente.")
        if not user_exists:
            cursor.execute("INSERT INTO rol (nombre) VALUES ('usuario')")
            logger.info("Rol 'usuario' creado exitosamente.")

        conn.commit()
        cursor.close()
        pool.putconn(conn)

    except Exception:
        logger.error("Error al asegurar la existencia de los roles:")
        logger.error(traceback.format_exc())
        raise

# Crear el pool de conexiones
try:
    logger.debug("=== Iniciando proceso de conexión (Postgres) ===")
    connection_pool = create_pool()
    ensure_roles_exist(connection_pool)
except Exception as e:
    logger.critical(f"Error crítico al inicializar el pool: {str(e)}")
    logger.critical(traceback.format_exc())
    sys.exit(1)
