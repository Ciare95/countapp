import psycopg2
from psycopg2 import pool
import sys
import logging
import traceback
import os
from urllib.parse import urlparse

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for DATABASE_URL from Render/Heroku environment
database_url = os.environ.get("DATABASE_URL")
if database_url:
    result = urlparse(database_url)
    dbconfig = {
        "user": result.username,
        "password": result.password,
        "host": result.hostname,
        "database": result.path[1:],
        "port": result.port,
    }
else:
    # Fallback to individual env vars for local development
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
            f"host={dbconfig['host']} "
            f"user={dbconfig['user']} "
            f"password={dbconfig['password']} "
            f"dbname={dbconfig['database']} "
            f"port={dbconfig['port']} "
            "client_encoding=utf8"
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

        # Create connection string with proper encoding
        conn_string = f"host={dbconfig['host']} user={dbconfig['user']} password={dbconfig['password']} dbname={dbconfig['database']} port={dbconfig['port']} client_encoding=utf8"
        
        connection_pool = pool.SimpleConnectionPool(
            1,                    # minconn
            15,                   # maxconn
            conn_string
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

def create_default_user(pool):
    """Creates a default admin user if no users exist."""
    try:
        conn = pool.getconn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            logger.info("No users found. Creating default admin user...")
            # Ensure the 'administrador' role exists and get its ID
            cursor.execute("SELECT id FROM rol WHERE nombre = 'administrador'")
            admin_role_id = cursor.fetchone()
            if admin_role_id:
                admin_role_id = admin_role_id[0]
                # Create the default admin user
                cursor.execute(
                    "INSERT INTO usuarios (nombre, contrasena, id_rol) VALUES (%s, %s, %s)",
                    ('admin', 'admin', admin_role_id)
                )
                conn.commit()
                logger.info("Default admin user created successfully (admin/admin).")
            else:
                logger.error("Could not find 'administrador' role to create default user.")

        cursor.close()
        pool.putconn(conn)

    except Exception:
        logger.error("Error creating default user:")
        logger.error(traceback.format_exc())
        raise

def initialize_schema():
    """Checks if the schema is initialized and creates it if not."""
    conn = None
    try:
        logger.debug("Verifying database schema...")
        conn = psycopg2.connect(
            f"host={dbconfig['host']} "
            f"user={dbconfig['user']} "
            f"password={dbconfig['password']} "
            f"dbname={dbconfig['database']} "
            f"port={dbconfig['port']} "
            "client_encoding=utf8"
        )
        cursor = conn.cursor()

        # Check if 'rol' table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rol');")
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.info("Schema not found. Initializing database...")
            with open('schema.sql', 'r') as f:
                cursor.execute(f.read())
            conn.commit()
            logger.info("Database initialized successfully.")
        else:
            logger.debug("Database schema already initialized.")

    except Exception as e:
        logger.error("Error initializing schema:")
        logger.error(traceback.format_exc())
        raise
    finally:
        if conn:
            conn.close()

# Crear el pool de conexiones
try:
    logger.debug("=== Iniciando proceso de conexión (Postgres) ===")
    initialize_schema()
    connection_pool = create_pool()
    ensure_roles_exist(connection_pool)
    create_default_user(connection_pool)
except Exception as e:
    logger.critical(f"Error crítico al inicializar el pool: {str(e)}")
    logger.critical(traceback.format_exc())
    sys.exit(1)
