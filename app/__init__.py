from flask import Flask, redirect, url_for, render_template, session, request
from flask_cors import CORS


from app.controllers import (
    producto_bp, categoria_bp, cliente_bp, usuario_bp, venta_bp,
    abono_bp, historial_bp, factura_bp, informe_bp, proveedor_bp, negocio_bp, fabricante_productos_bp, 
    fabricante_ingredientes_bp, fabricante_utilidades_bp,
)
from .db import connection_pool
from flask_login import LoginManager, login_required, current_user
from app.models.usuarios import Usuario

def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = 'Ciarentcity2'
    CORS(app)
   
    
    # Configuración del Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "usuario.login"  # Esto redirigirá a la ruta de login cuando sea necesario
    
    @login_manager.user_loader
    def load_user(user_id):
        conexion = connection_pool.getconn()
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = "SELECT * FROM usuarios WHERE id = %s"
            cursor.execute(sql, (user_id,))
            resultado = cursor.fetchone()
            if resultado:
                return Usuario(
                    id=resultado[0],
                    nombre=resultado[1],
                    contrasena=resultado[2],
                    id_rol=resultado[3]
                )
            return None
        finally:
            if cursor:
                cursor.close()
            if 'conexion' in locals():
                connection_pool.putconn(conexion)
            
    
    @app.before_request
    def clear_session_if_needed():
        if not current_user.is_authenticated and request.endpoint != 'usuario.login':
            session.clear()      

    # Registrar los Blueprints
    blueprints = [
        (producto_bp, "/productos"),
        (categoria_bp, "/categorias"),
        (cliente_bp, "/clientes"),
        (usuario_bp, "/usuarios"),
        (venta_bp, "/ventas"),
        (abono_bp, "/abonos"),
        (historial_bp, "/historial"),
        (factura_bp, "/facturas"),
        (informe_bp, "/informes"),
        (proveedor_bp, "/proveedores"),
        (negocio_bp, "/negocios"),
        (fabricante_productos_bp, "/fabricante_productos"),
        (fabricante_ingredientes_bp, "/fabricante_ingredientes"),
        (fabricante_utilidades_bp, "/fabricante_utilidades"),
    ]
    
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    @app.route("/", methods=["GET", "POST"])
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return redirect(url_for('usuario.login'))

    @app.route("/index", methods=["GET", "POST"])
    @login_required
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('usuario.login'))
        try:
            connection = connection_pool.getconn()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM categorias")
            categorias = cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener las categorías: {e}")
            categorias = []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection_pool.putconn(connection)
        return render_template("index.html", categorias=categorias)

    return app

app = create_app()
