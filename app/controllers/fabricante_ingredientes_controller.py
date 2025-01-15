from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.productos_fabricados import ProductoFabricado
from app.models.ingredientes_productos import IngredienteProducto
from app.models.ingrediente import Ingrediente
from app.controllers.fabricante_utilidades_controller import convertir_unidad
from app.models.facturas_fabricacion import FacturaFabricacion
from app.models.ingredientes_factura import IngredienteFactura
import decimal
from app.db import connection_pool as db

fabricante_ingredientes_bp = Blueprint('fabricante_ingredientes', __name__)

def get_conversion_factor(unidad_origen, unidad_destino):
    conversiones = {
            'gramos': { 'kilos': 0.001, 'litros': 0.001, 'mililitros': 1, 'cc': 1, 'galon': 0.000264172, 'garrafa': 0.00005 },
            'kilos': { 'gramos': 1000, 'litros': 1, 'mililitros': 1000, 'cc': 1000, 'galon': 0.264172, 'garrafa': 0.05 },
            'litros': { 'gramos': 1000, 'kilos': 1, 'mililitros': 1000, 'cc': 1000, 'galon': 0.264172, 'garrafa': 0.05 },
            'mililitros': { 'gramos': 1, 'kilos': 0.001, 'litros': 0.001, 'cc': 1, 'galon': 0.000264172, 'garrafa': 0.00005 },
            'cc': { 'gramos': 1, 'kilos': 0.001, 'litros': 0.001, 'mililitros': 1, 'galon': 0.000264172, 'garrafa': 0.00005 },
            'galon': { 'gramos': 4000, 'kilos': 4, 'litros': 4, 'mililitros': 4000, 'cc': 4000, 'garrafa': 0.2 },
            'garrafa': { 'gramos': 20000, 'kilos': 20, 'litros': 20, 'mililitros': 20000, 'cc': 20000, 'galon': 5 }
    }
    return conversiones.get(unidad_origen, {}).get(unidad_destino, 1)




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
        costo_empaque = request.form.get('costo_empaque')

        # Validar campos requeridos
        required_fields = {
            'costo_factura': costo_factura,
            'unidad_medida': unidad_medida,
            'cantidad_ing': cantidad_ing,
            'cantidad_factura': cantidad_factura,
            'costo_ing_por_producto': costo_ing_por_producto,
            'costo_empaque': costo_empaque
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
                'costo_ing_por_producto': decimal.Decimal(costo_ing_por_producto),
                'costo_empaque': decimal.Decimal(costo_empaque)
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
            valores_numericos['costo_ing_por_producto'],
            valores_numericos['costo_empaque']
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
        

@fabricante_ingredientes_bp.route('/factura_ingredientes', methods=['GET'])
def factura_ingredientes():
    connection = db.get_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, nombre FROM proveedores")
        proveedores = cursor.fetchall()
        
        cursor.execute("SELECT id, nombre FROM ingredientes")
        ingredientes = cursor.fetchall()
    connection.close()
    
    return render_template('fabricante/factura_ingredientes.html', 
                         proveedores=proveedores,
                         ingredientes=ingredientes)
    

@fabricante_ingredientes_bp.route('/crear_factura', methods=['POST'])
def crear_factura():
    try:
        numero_factura = request.form['numero_factura']
        id_proveedor = request.form['proveedor']
        total = request.form['total']
        
        connection = db.get_connection()
        with connection.cursor() as cursor:
            # Crear la factura en facturas_fabricacion
            query = """
            INSERT INTO facturas_fabricacion (numero_factura, id_proveedor, total)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (numero_factura, id_proveedor, total))
            id_factura = cursor.lastrowid
            
            connection.commit()
        connection.close()
        
        return jsonify({'success': True, 'id_factura': id_factura})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

@fabricante_ingredientes_bp.route('/agregar_ingrediente_factura', methods=['POST'])
def agregar_ingrediente_factura():
    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            # Verificar que la factura existe
            check_query = "SELECT id FROM facturas_fabricacion WHERE id = %s"
            cursor.execute(check_query, (request.form['id_factura'],))
            if not cursor.fetchone():
                raise Exception("La factura no existe")
            
            # Calcular el total
            cantidad = float(request.form['cantidad'])
            precio_unitario = float(request.form['precio_unitario'])
            total = round(cantidad * precio_unitario, 2)
            
            # Insertar en ingredientes_factura
            query = """
            INSERT INTO ingredientes_factura 
            (id_factura, id_ingrediente, cantidad, precio_unitario, medida_ingrediente)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                request.form['id_factura'],
                request.form['id_ingrediente'],
                request.form['cantidad'],
                request.form['precio_unitario'],
                request.form['unidad_medida']
            ))
            
            # Obtener datos necesarios del ingrediente_producto
            obtener_datos_query = """
            SELECT unidad_medida, cantidad_ing, cantidad_factura
            FROM ingredientes_producto
            WHERE ingrediente_id = %s
            """
            cursor.execute(obtener_datos_query, (request.form['id_ingrediente'],))
            resultado = cursor.fetchone()
            if not resultado:
                raise Exception("No se encontraron datos del ingrediente")
            
            unidad_medida, cantidad_ing, cantidad_factura = resultado
            factor_conversion = get_conversion_factor(unidad_medida, cantidad_factura)
            cantidad_convertida = float(cantidad_ing) * factor_conversion
            
            if cantidad_convertida == 0:
                raise Exception("Error en la conversión de unidades")
            
            # Calcular el costo por producto
            costo_ing_por_producto = round(precio_unitario * cantidad_convertida, 2)
            
            # Actualizar costos en ingredientes_producto
            update_query = """
            UPDATE ingredientes_producto 
            SET costo_factura = %s,
                costo_ing_por_producto = %s
            WHERE ingrediente_id = %s
            """
            cursor.execute(update_query, (
                precio_unitario,
                costo_ing_por_producto,
                request.form['id_ingrediente']
            ))
            
            connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Ingrediente agregado y costos actualizados correctamente',
                'total': total,
                'costo_calculado': costo_ing_por_producto
            })
            
    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if connection:
            connection.close()



@fabricante_ingredientes_bp.route('/mostrar_facturas')
def mostrar_facturas():
    try:
        facturas = FacturaFabricacion.obtener_todos()
        
        return render_template('fabricante/listar_facturas.html', facturas=facturas)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('fabricante/listar_facturas.html', facturas=[], error="Error al cargar facturas")
    
    
@fabricante_ingredientes_bp.route('/ver_factura/<int:id_factura>')
def ver_factura(id_factura):
    try:
        ingredientes = IngredienteFactura.obtener_por_id(id_factura)
        
        return render_template('fabricante/ver_factura.html', ingredientes=ingredientes)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('fabricante/ver_factura.html', ingredientes=[], error="Error al cargar la factura")