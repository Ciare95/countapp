from flask import Blueprint, request, render_template, jsonify
from app.models.informe import InformeModel
from app.models.facturas import FacturaModel
from flask_login import login_required
from app.controllers.usuario_controller import administrador_requerido

informe_bp = Blueprint('informes', __name__)


@informe_bp.route('/ingresos_egresos', methods=['GET'])
@login_required
@administrador_requerido  # Solo los administradores pueden acceder a esta ruta
def ingresos_egresos():
    try:
        # Obtener filtros de fecha
        filtro_fecha = request.args.get('fecha')  # yyyy-mm-dd
        filtro_mes = request.args.get('mes')  # yyyy-mm
        filtro_anio = request.args.get('anio')  # yyyy

        # Construcción de la cláusula WHERE y parámetros
        condiciones = []
        parametros = {}

        if filtro_fecha:
            condiciones.append("DATE(v.fecha_venta) = %(fecha)s")
            parametros['fecha'] = filtro_fecha
        elif filtro_mes:
            condiciones.append("MONTH(v.fecha_venta) = %(mes)s AND YEAR(v.fecha_venta) = %(anio_mes)s")
            parametros['mes'] = int(filtro_mes.split("-")[1])
            parametros['anio_mes'] = int(filtro_mes.split("-")[0])
        elif filtro_anio:
            condiciones.append("YEAR(v.fecha_venta) = %(anio)s")
            parametros['anio'] = int(filtro_anio)

        where_clause = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        # Obtener datos del modelo
        total_ingresos = InformeModel.obtener_ingresos(where_clause, parametros)
        total_egresos = InformeModel.obtener_egresos(where_clause, parametros)

        # Calcular ganancia neta
        ganancia_neta = float(total_ingresos.replace('$', '').replace('.', '').replace(',', '.')) - float(total_egresos.replace('$', '').replace('.', '').replace(',', '.'))

        # Formatear la ganancia neta
        ganancia_neta = InformeModel.formato_peso_colombiano(ganancia_neta)

        # Renderizar plantilla
        return render_template('informes/ingresos_egresos.html',
                            total_egresos=total_egresos,
                            total_ingresos=total_ingresos,
                            ganancia_neta=ganancia_neta,
                            fecha=filtro_fecha,
                            mes=filtro_mes,
                            anio=filtro_anio)
    except Exception as e:
        print(f"Error al obtener ingresos y egresos: {e}")
        return "Error interno", 500


@informe_bp.route('/registro_ingresos', methods=['GET'])
def registro_ingresos():
    try:
        return render_template('informes/registro_de_ingresos.html')
    except Exception as e:
        print(f"Error al cargar la página de registro de ingresos: {e}")
        return "Error interno", 500


@informe_bp.route('/registro_ingresos/otros_egresos', methods=['POST'])
def registrar_otros_egresos():
    try:
        data = request.json
        descripcion = data['descripcion']
        valor = data['valor']

        # Registrar el egreso utilizando el modelo
        InformeModel.registrar_otro_egreso(descripcion, valor)

        return jsonify({'message': 'Egreso registrado exitosamente'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error al registrar egreso'}), 500


@informe_bp.route('/registro_ingresos/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.json
    numero_factura = data.get('numero_factura')
    id_producto = data.get('id_producto')
    cantidad = data.get('cantidad')
    precio_compra = data.get('precio_compra')
    precio_venta = data.get('precio_venta')
    porcentaje_iva = data.get('porcentaje_iva', 0)  # Nuevo campo, default 0 si no se proporciona

    try:
        # Obtener el ID de la factura usando el numero_factura
        id_factura = FacturaModel.obtener_id_por_numero_factura(numero_factura)
        if not id_factura:
            return jsonify({'error': 'Número de factura no encontrado'}), 404

        # Agregar producto a la factura
        resultado = FacturaModel.agregar_producto_a_factura(
            id_factura, id_producto, cantidad, precio_compra, precio_venta, porcentaje_iva  # Agregado porcentaje_iva
        )
        if resultado:
            return jsonify({'message': 'Producto agregado correctamente'}), 200
        else:
            return jsonify({'error': 'El producto ya está en esta factura'}), 400  # Cambio aquí para indicar que ya está
    except Exception as e:
        print(e)
        return jsonify({'error': 'Error al procesar la solicitud'}), 500
    
    
@informe_bp.route("/obtener_egresos", methods=['GET'])
def obtener_egresos():
    try:
        egresos = InformeModel.listar_otros_egresos()
        return render_template("informes/otros_egresos.html", egresos=egresos or [])
    except Exception as e:
        print(f"Error: {e}")
        return render_template("informes/otros_egresos.html", egresos=[])
