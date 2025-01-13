from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db import connection_pool as db
from app.models.productos_fabricados import ProductoFabricado


fabricante_productos_bp = Blueprint('fabricante_productos', __name__)



@fabricante_productos_bp.route('/fabricante')
def listar_productos_fabricados():
    productos = ProductoFabricado.obtener_todos()
    return render_template("fabricante/index.html", productos=productos)




# Rutas principales del módulo fabricante
@fabricante_productos_bp.route('/')
def index():
    # Mostrar todos los productos fabricados
    productos = ProductoFabricado.obtener_todos()
    return render_template('fabricante/index.html', productos=productos)


@fabricante_productos_bp.route('/crear', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        # Crear un nuevo producto fabricado
        nombre = request.form.get('nombre')
        unidad_medida = request.form.get('unidad_medida')
        cantidad_producida = request.form.get('cantidad_producida')

        if not nombre or not unidad_medida or not cantidad_producida:
            return redirect(url_for('fabricante_productos.crear_producto'))

        ProductoFabricado.crear(
            nombre=nombre,
            unidad_medida=unidad_medida,
            costo_total=0,  # Inicialmente 0, se calculará con los ingredientes
            precio_venta=0,  # Valor por defecto
            cantidad_producida=cantidad_producida,
        )

        return redirect(url_for('fabricante_productos.index'))

    return render_template('fabricante/crear_producto.html')


@fabricante_productos_bp.route('/<int:producto_id>/editar', methods=['GET', 'POST'])
def editar_producto(producto_id):
    # Editar un producto fabricado existente
    producto = ProductoFabricado.obtener_por_id(producto_id)

    if not producto:
        return redirect(url_for('fabricante_productos.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        unidad_medida = request.form.get('unidad_medida')
        cantidad_producida = request.form.get('cantidad_producida')
        precio_venta = request.form.get('precio_venta')

        if not nombre or not unidad_medida or not cantidad_producida or not precio_venta:
            return redirect(url_for('fabricante_productos.editar_producto', producto_id=producto_id))

        ProductoFabricado.actualizar(
            producto_id=producto_id,
            nombre=nombre,
            unidad_medida=unidad_medida,
            cantidad_producida=cantidad_producida,
            precio_venta=precio_venta
        )

        return redirect(url_for('fabricante_productos.index'))

    return render_template('fabricante/editar_producto.html', producto=producto)



@fabricante_productos_bp.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    datos = request.get_json()
    
    for ingrediente in datos['ingredientes']:
        query = """
            INSERT INTO ingredientes_producto 
            (producto_id, ingrediente_id, cantidad_por_unidad, unidad_cantidad, 
             costo_unitario, unidad_costo, cantidad_original, unidad_original)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            cantidad_por_unidad = VALUES(cantidad_por_unidad),
            unidad_cantidad = VALUES(unidad_cantidad),
            costo_unitario = VALUES(costo_unitario),
            unidad_costo = VALUES(unidad_costo),
            cantidad_original = VALUES(cantidad_original),
            unidad_original = VALUES(unidad_original)
        """
        values = (
            datos['producto_id'],
            ingrediente['ingrediente_id'],
            ingrediente['cantidad_por_unidad'],
            ingrediente['unidad_cantidad'],
            ingrediente['costo_unitario'],
            ingrediente['unidad_costo'],
            ingrediente['cantidad_original'],
            ingrediente['unidad_original']
        )
        
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
        connection.commit()
        connection.close()
    
    return jsonify({'success': True})

    




@fabricante_productos_bp.route('/<int:producto_id>/eliminar', methods=['POST'])
def eliminar_producto(producto_id):
    # Eliminar un producto fabricado
    producto = ProductoFabricado.obtener_por_id(producto_id)

    if not producto:
        return redirect(url_for('fabricante.index'))

    ProductoFabricado.eliminar(producto_id)
    return redirect(url_for('fabricante.index'))



@fabricante_productos_bp.route('/ver_producto_fabricado/<int:producto_id>', methods=['GET'])
def ver_producto_fabricado(producto_id):
    # Obtener el producto por ID
    producto = ProductoFabricado.obtener_por_id(producto_id)
    if not producto:
        return redirect(url_for('fabricante.index'))

    # Obtener los ingredientes asociados al producto
    ingredientes = producto.obtener_ingredientes()

    # Preparar los datos para la plantilla
    ingredientes_data = []
    for ingrediente in ingredientes:
        ingredientes_data.append({
            'nombre': ingrediente['nombre'],
            'costo_factura': ingrediente['costo_factura'],
            'costo_ing_por_producto': ingrediente['costo_ing_por_producto'],
            'unidad_medida': ingrediente['unidad_medida'],
            'cantidad_ing': ingrediente['cantidad_ing'],
            'cantidad_factura': ingrediente['cantidad_factura'],
        })

    # Renderizar la plantilla con los datos
    return render_template(
        'fabricante/ver_producto_fabricado.html',
        producto=producto,
        ingredientes=ingredientes_data
    )






