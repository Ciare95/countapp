from flask import jsonify, render_template, request, redirect, url_for, Blueprint, flash
from app.models.categorias import Categoria
from app.models.productos import Producto
from app.db import connection_pool
from flask_login import login_required
from app.controllers.usuario_controller import administrador_requerido

# Definir el Blueprint para productos
producto_bp = Blueprint("producto", __name__, url_prefix="/productos")


@producto_bp.route('/productos', methods=['GET'])
def listar_productos():
    producto = Producto()
    productos = producto.obtener_todos()
    categoria = Categoria()
    categorias = categoria.obtener_categorias()
    return render_template('productos/listar.html', productos=productos, categorias=categorias)


@producto_bp.route("/crear", methods=['POST'])
@login_required
@administrador_requerido
def crear_producto():
    if request.method == 'POST':
        producto = Producto()
        producto.nombre = request.form['nombre']
        producto.id_categorias = request.form['categoria']
        producto.cantidad = request.form['stock']
        producto.precio_compra = request.form['precio_compra']
        producto.precio = request.form['precio']
        
        if producto.crear_producto():
            flash("Producto creado correctamente.", "success")
        else:
            flash("Error al crear el producto. Inténtalo de nuevo.", "error")
    return redirect(url_for('producto.listar_productos'))


@producto_bp.route("/editar/<int:id>", methods=['GET', 'POST'])
@login_required
@administrador_requerido
def editar_producto(id):
    producto = Producto()
    producto.obtener_por_id(id)
    
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.id_categorias = request.form['categoria']
        producto.cantidad = request.form['stock']
        producto.precio_compra = request.form['precio_compra']
        producto.precio = request.form['precio']
        
        if producto.actualizar_producto():
            flash("Producto actualizado correctamente.", "success")
        else:
            flash("Error al actualizar el producto. Inténtalo de nuevo.", "error")
    return redirect(url_for('producto.listar_productos'))


@producto_bp.route("/eliminar/<int:id>", methods=['POST'])
@login_required
@administrador_requerido  # Solo los administradores pueden acceder a esta ruta
def eliminar_producto(id):
    producto = Producto(id=id)
    try:
        if producto.eliminar_producto():
            flash("Producto eliminado correctamente.", "success")
        else:
            flash("No se pudo eliminar el producto. Inténtalo de nuevo.", "error")
    except Exception as e:
        if "foreign key constraint fails" in str(e).lower():
            flash(
                "El producto no puede ser eliminado porque tiene relaciones activas con otras tablas.",
                "error",
            )
        else:
            flash(f"Error inesperado: {str(e)}", "error")
    return redirect(url_for('producto.listar_productos'))


@producto_bp.route('/buscar/<termino>', methods=['GET'])
def buscar_producto(termino):
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, nombre, precio FROM productos
            WHERE nombre LIKE %s OR id LIKE %s
        """
        cursor.execute(query, (f"%{termino}%", f"%{termino}%"))
        productos = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify(productos)
    except Exception as e:
        flash(f"Error al buscar el producto: {str(e)}", "error")
        return jsonify({"error": str(e)}), 500


@producto_bp.route('/registro_ingresos/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.get_json()
    
    # Validación inicial de los datos recibidos
    required_fields = ['id_factura', 'id_producto', 'cantidad', 'precio_compra', 'precio_venta']
    for field in required_fields:
        if field not in data:
            flash(f"Falta el campo obligatorio: {field}", "error")
            return jsonify({"error": f"Falta el campo obligatorio: {field}"}), 400

    id_factura = data['id_factura']
    id_producto = data['id_producto']
    cantidad = data['cantidad']
    precio_compra = data['precio_compra']
    precio_venta = data['precio_venta']

    try:
        # Obtener conexión desde el pool
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor()

        # Iniciar una transacción
        conexion.start_transaction()

        # Insertar en la tabla intermedia productos_factura
        sql_insert = """
        INSERT INTO productos_factura (id_factura, id_producto, cantidad, precio_compra, precio_venta)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (id_factura, id_producto, cantidad, precio_compra, precio_venta))

        # Actualizar el stock del producto en la tabla productos
        sql_update_stock = """
        UPDATE productos
        SET stock = stock + %s
        WHERE id = %s
        """
        cursor.execute(sql_update_stock, (cantidad, id_producto))  # Aquí sumamos porque estás ingresando productos a stock

        # Confirmar la transacción
        conexion.commit()

        flash("Producto agregado exitosamente.", "success")
        return jsonify({"message": "Producto agregado exitosamente"}), 200

    except Exception as e:
        if 'conexion' in locals() and conexion.is_connected():
            conexion.rollback()  # Revertir la transacción si hay un error
        flash(f"Error al agregar producto: {str(e)}", "error")
        return jsonify({"error": f"Error al agregar producto: {str(e)}"}), 500

    finally:
        # Asegurar que la conexión sea cerrada
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion.is_connected():
            conexion.close()
