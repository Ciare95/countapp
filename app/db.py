import mysql.connector
from mysql.connector import pooling
import sys
import logging
import traceback
import os

# Configuración de logging (mantén la misma que tienes)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Forzar el uso del driver puro Python
mysql.connector.HAVE_CEXT = False

logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(f"Python path: {sys.path}")
logger.debug(f"MySQL Connector version: {mysql.connector.__version__}")
logger.debug(f"Using pure Python implementation: {not mysql.connector.HAVE_CEXT}")

dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "sistema_papeleria",
    "port": 3306,
    "connection_timeout": 30,
    "raise_on_warnings": True,
    "use_pure": True  # Forzar el uso de la implementación pura Python
}

def test_basic_connection():
    try:
        # Intentar crear una conexión básica primero
        logger.debug("Intentando conexión básica sin pool...")
        conn = mysql.connector.connect(
            host=dbconfig['host'],
            user=dbconfig['user'],
            password=dbconfig['password'],
            database=dbconfig['database'],
            port=dbconfig['port']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        logger.debug(f"Versión del servidor MySQL: {version}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error("Error en conexión básica:")
        logger.error(traceback.format_exc())
        return False

def create_pool():
    try:
        # Probar conexión básica primero
        if not test_basic_connection():
            raise Exception("La conexión básica falló, no se intentará crear el pool")

        logger.debug("Intentando crear pool de conexiones...")
        
        # Crear el pool con configuración mínima primero
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            host=dbconfig['host'],
            user=dbconfig['user'],
            password=dbconfig['password'],
            database=dbconfig['database']
        )
        
        logger.info("Pool de conexiones creado exitosamente")
        
        # Probar obtener una conexión del pool
        try:
            test_conn = pool.get_connection()
            test_conn.close()
            logger.debug("Prueba de conexión del pool exitosa")
        except Exception as pool_test_error:
            logger.error(f"Error al probar conexión del pool: {pool_test_error}")
            raise
            
        return pool
        
    except mysql.connector.Error as err:
        logger.error("Error específico de MySQL:")
        logger.error(f"Error code: {err.errno if hasattr(err, 'errno') else 'N/A'}")
        logger.error(f"SQLSTATE: {err.sqlstate if hasattr(err, 'sqlstate') else 'N/A'}")
        logger.error(f"Error message: {str(err)}")
        raise
    except Exception as e:
        logger.error("Error general:")
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Mensaje: {str(e)}")
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        raise

# Crear el pool de conexiones
try:
    logger.debug("=== Iniciando proceso de conexión ===")
    connection_pool = create_pool()
except Exception as e:
    logger.critical(f"Error crítico al inicializar el pool: {str(e)}")
    logger.critical("Detalles completos del error:")
    logger.critical(traceback.format_exc())
    sys.exit(1)