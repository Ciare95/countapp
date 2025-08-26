from contextlib import contextmanager
from app.db import connection_pool
import logging
import traceback

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """
    Context manager para obtener y liberar conexiones de la pool de manera segura.
    """
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except Exception as e:
        logger.error(f"Error al obtener conexión de la pool: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        if connection:
            try:
                connection_pool.putconn(connection)
            except Exception as e:
                logger.error(f"Error al devolver conexión a la pool: {e}")
                logger.error(traceback.format_exc())

@contextmanager
def get_db_cursor():
    """
    Context manager para obtener y liberar cursor de manera segura.
    """
    connection = None
    cursor = None
    try:
        connection = connection_pool.getconn()
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Error en operación de base de datos: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                logger.error(f"Error al cerrar cursor: {e}")
        if connection:
            try:
                connection_pool.putconn(connection)
            except Exception as e:
                logger.error(f"Error al devolver conexión a la pool: {e}")

def execute_query(query, params=None):
    """
    Ejecuta una consulta y retorna los resultados.
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()

def execute_update(query, params=None):
    """
    Ejecuta una consulta de actualización (INSERT, UPDATE, DELETE).
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount
