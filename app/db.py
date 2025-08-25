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
    # Ensure SSL mode is set for Render connections
    if "render.com" in database_url and "sslmode" not in database_url:
        database_url += "?sslmode=require"
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

        # Use the full database_url if available, otherwise construct it
        if database_url:
            conn_string = database_url
        else:
            # Create connection string with proper encoding for local dev
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
    """Checks and initializes the database schema, including partial updates."""
    try:
        logger.debug("Verifying database schema...")
        
        # Create a fresh connection for schema initialization
        conn = psycopg2.connect(
            f"host={dbconfig['host']} "
            f"user={dbconfig['user']} "
            f"password={dbconfig['password']} "
            f"dbname={dbconfig['database']} "
            f"port={dbconfig['port']} "
            "client_encoding=utf8"
        )
        cursor = conn.cursor()

        # Check for each required table
        required_tables = ['rol', 'usuarios', 'clientes', 'ventas', 'categorias', 'productos', 'detalle_ventas', 'abonos', 'facturas', 'proveedores', 'otros_egresos']
        missing_tables = []
        
        for table in required_tables:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}');")
            if not cursor.fetchone()[0]:
                missing_tables.append(table)

        if missing_tables:
            logger.info(f"Missing tables detected: {missing_tables}. Creating missing tables...")
            with open('schema_postgres.sql', 'r') as f:
                schema_sql = f.read()
            
            # Split into individual statements
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            # Execute statements in proper order with explicit commits
            successful_creations = 0
            for stmt in statements:
                try:
                    # Only execute statements for missing tables
                    if any(table in stmt.lower() for table in missing_tables):
                        # Skip problematic tables that reference non-existent tables
                        if 'ingredientes_producto' in stmt and 'productos_fabricados' not in missing_tables:
                            logger.debug(f"Skipping problematic table creation: ingredientes_producto")
                            continue
                        cursor.execute(stmt)
                        conn.commit()  # Explicit commit after each statement
                        logger.debug(f"Executed and committed: {stmt}")
                        successful_creations += 1
                except psycopg2.errors.DuplicateTable:
                    logger.debug(f"Table already exists, skipping: {stmt.split()[2]}")
                    conn.rollback()  # Clear any transaction state
                    continue
                except Exception as e:
                    logger.error(f"Error executing schema statement: {e}")
                    logger.error(f"Failed statement: {stmt}")
                    conn.rollback()  # Clear any transaction state
                    continue
            
            logger.info(f"Successfully executed {successful_creations} schema statements")
            
            # Verify tables were created
            try:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                existing_tables = [table[0] for table in cursor.fetchall()]
                logger.debug(f"Tables after creation: {existing_tables}")
            except Exception as e:
                logger.error(f"Error verifying tables: {e}")
            
        else:
            logger.debug("All required tables exist.")

        # Check and add missing columns
        try:
            logger.debug("Checking for missing columns in existing tables...")
            check_and_add_missing_columns(conn)
            logger.debug("Finished checking for missing columns.")
        except Exception as e:
            logger.error(f"Error checking/adding columns: {e}")
            conn.rollback()

    except Exception as e:
        logger.error("Error initializing schema:")
        logger.error(traceback.format_exc())
        # Don't raise the exception to allow the application to continue
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def check_and_add_missing_columns(conn):
    """Check for missing columns in existing tables and add them if needed."""
    cursor = conn.cursor()
    try:
        # Columnas requeridas para la tabla productos
        required_columns = {
            'productos': [
                ('stock', 'INTEGER'),
                ('precio_compra', 'DECIMAL(10,2)'),
                ('es_servicio', 'BOOLEAN DEFAULT FALSE')
            ]
        }
        
        for table_name, columns in required_columns.items():
            # Verificar si la tabla existe
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}');")
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                for column_name, column_type in columns:
                    # Verificar si la columna existe
                    cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table_name}' AND column_name = '{column_name}');")
                    column_exists = cursor.fetchone()[0]
                    
                    if not column_exists:
                        logger.info(f"Adding missing column '{column_name}' to table '{table_name}'...")
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
                        logger.info(f"Column '{column_name}' added successfully to table '{table_name}'")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"Error checking/adding missing columns: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()

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
