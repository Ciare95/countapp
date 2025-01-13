from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.productos_fabricados import ProductoFabricado
from app.models.ingredientes_productos import IngredienteProducto
from app.models.ingrediente import Ingrediente
from app.controllers.fabricante_utilidades_controller import convertir_unidad
import decimal

fabricante_ingredientes_bp = Blueprint('fabricante_ingredientes', __name__)



@fabricante_ingredientes_bp.route('/crear_ingrediente', methods=['GET', 'POST'])
def crear_ingrediente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')

        # Llamamos al método para crear el ingrediente
        Ingrediente.crear(nombre, descripcion)

        return redirect(url_for('fabricante_ingredientes.listar_ingredientes'))

    return render_template('fabricante/crear_ingrediente.html')


@fabricante_ingredientes_bp.route('/listar_ingredientes')
def listar_ingredientes():
    # Obtener todos los ingredientes
    ingredientes = Ingrediente.obtener_todos()
    return render_template('fabricante/listar_ingredientes.html', ingredientes=ingredientes)


@fabricante_ingredientes_bp.route('/editar_ingrediente/<int:id>', methods=['GET', 'POST'])
def editar_ingrediente(id):
    ingrediente = Ingrediente.obtener_por_id(id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        Ingrediente.actualizar(id, nombre, descripcion)
        return redirect(url_for('fabricante_ingredientes.listar_ingredientes'))
    return render_template('fabricante/editar_ingredientes.html', ingrediente=ingrediente)

@fabricante_ingredientes_bp.route('/eliminar_ingrediente/<int:id>', methods=['POST'])
def eliminar_ingrediente(id):
    Ingrediente.eliminar(id)
    return redirect(url_for('fabricante_ingredientes.listar_ingredientes'))



@fabricante_ingredientes_bp.route('/<int:producto_id>/asignar_ingredientes', methods=['GET', 'POST'])
def asignar_ingredientes(producto_id):
    producto = ProductoFabricado.obtener_por_id(producto_id)
    if not producto:
        return redirect(url_for('fabricante_productos.index'))


    ingredientes = Ingrediente.obtener_todos()
    relaciones_existentes = IngredienteProducto.obtener_por_producto(producto.id)
    
    return render_template('fabricante/asignar_ingredientes.html',
                         producto=producto,
                         ingredientes=ingredientes,
                         relaciones=relaciones_existentes)
    




@fabricante_ingredientes_bp.route('/guardar_ingredientes', methods=['POST'])
def guardar_ingredientes():

    try:
        datos = request.get_json()
        print(datos)
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400

        producto_id = datos.get('producto_id')
        ingredientes = datos.get('ingredientes', [])

        if not producto_id or not ingredientes:
            return jsonify({'error': 'Datos incompletos'}), 400

        for ingrediente in ingredientes:
            Ingrediente.guardar_ingrediente({
                'producto_id': producto_id,
                'ingrediente_id': ingrediente['id'],
                'costo_factura': ingrediente['costo_factura'],
                'costo_ing_por_producto': ingrediente['costo_ing_por_producto'],
                'unidad_medida': ingrediente['unidad_medida'],
                'cantidad_ing': ingrediente['cantidad_ing'],
                'cantidad_factura': ingrediente['cantidad_factura']
            })

        # Actualizar el costo total del producto fabricado
        costo_total = Ingrediente.obtener_costo_total(producto_id)
        ProductoFabricado.actualizar_costo_total(producto_id, costo_total)

        return jsonify({'message': 'Ingredientes guardados correctamente'}), 200
    

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Ocurrió un error al guardar los ingredientes'}), 500


        
@fabricante_ingredientes_bp.route('/editar', methods=['POST'])
def editar():
    try:
        print("Datos recibidos:", request.form)  # Log de datos recibidos
        ingrediente_id = request.form.get('ingrediente_id')
        print("ID del ingrediente:", ingrediente_id)  # Log del ID específico
        
        # Validar ID primero
        try:
            ingrediente_id = int(ingrediente_id)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "ID de ingrediente inválido"
            }), 400

        # Obtener resto de campos
        costo_factura = request.form.get('costo_factura')
        unidad_medida = request.form.get('unidad_medida')
        cantidad_ing = request.form.get('cantidad_ing')
        cantidad_factura = request.form.get('cantidad_factura')
        costo_ing_por_producto = request.form.get('costo_ing_por_producto')

        # Validar campos requeridos
        required_fields = {
            'costo_factura': costo_factura,
            'unidad_medida': unidad_medida,
            'cantidad_ing': cantidad_ing,
            'cantidad_factura': cantidad_factura,
            'costo_ing_por_producto': costo_ing_por_producto
        }

        missing_fields = [k for k, v in required_fields.items() if not v]
        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            }), 400

        # Validar unidades de medida
        valid_units = ['gramos', 'kilos', 'litros', 'mililitros', 'cc', 'galon', 'garrafa']
        if unidad_medida not in valid_units or cantidad_factura not in valid_units:
            return jsonify({
                "success": False,
                "message": "Unidad de medida inválida"
            }), 400

        # Convertir y validar valores numéricos
        try:
            valores_numericos = {
                'costo_factura': decimal.Decimal(costo_factura),
                'cantidad_ing': decimal.Decimal(cantidad_ing),
                'costo_ing_por_producto': decimal.Decimal(costo_ing_por_producto)
            }

            # Validar que los valores sean positivos
            for campo, valor in valores_numericos.items():
                if valor <= 0:
                    return jsonify({
                        "success": False,
                        "message": f"El campo {campo} debe ser mayor que 0"
                    }), 400

        except decimal.InvalidOperation:
            return jsonify({
                "success": False,
                "message": "Valores numéricos inválidos"
            }), 400

        # Actualizar el registro
        IngredienteProducto.actualizar(
            ingrediente_id,
            valores_numericos['costo_factura'],
            unidad_medida,
            valores_numericos['cantidad_ing'],
            cantidad_factura,
            valores_numericos['costo_ing_por_producto']
        )
        
        return jsonify({
            "success": True,
            "message": "Ingrediente actualizado correctamente"
        })

    except Exception as e:
        print(f"Error al actualizar ingrediente: {e}")
        return jsonify({
            "success": False,
            "message": f"Error al actualizar: {str(e)}"
        }), 500

