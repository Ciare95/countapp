from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from app.models.historial import HistorialModel
from app.db import connection_pool  

historial_bp = Blueprint('historiales', __name__)

@historial_bp.route('/historial_general', methods=['GET'])
def historial_general():
    try:
        # Obtener filtros de fecha
        filtro_fecha = request.args.get('fecha')  # yyyy-mm-dd
        filtro_mes = request.args.get('mes')      # yyyy-mm
        filtro_anio = request.args.get('anio')    # yyyy

        # Si no hay ningún filtro, usar la fecha actual
        if not filtro_fecha and not filtro_mes and not filtro_anio:
            filtro_fecha = datetime.now().strftime('%Y-%m-%d')

        # Construcción de la cláusula WHERE y parámetros
        condiciones = []
        parametros = {}

        if filtro_fecha:
            condiciones.append("DATE(v.fecha_venta) = %(fecha)s")
            parametros['fecha'] = filtro_fecha
        elif filtro_mes:
            mes = int(filtro_mes.split("-")[1])
            anio = int(filtro_mes.split("-")[0])
            condiciones.append("MONTH(v.fecha_venta) = %(mes)s AND YEAR(v.fecha_venta) = %(anio_mes)s")
            parametros['mes'] = mes
            parametros['anio_mes'] = anio
        elif filtro_anio:
            condiciones.append("YEAR(v.fecha_venta) = %(anio)s")
            parametros['anio'] = int(filtro_anio)

        where_clause = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
        
        # Obtener las ventas filtradas y totales
        ventas, totales = HistorialModel.obtener_ventas_generales(where_clause, parametros)
        
        return render_template('ventas/historial_general.html',
                    ventas=ventas,
                    totales=totales,
                    fecha=filtro_fecha,
                    mes=filtro_mes,
                    anio=filtro_anio)

    except Exception as e:
        print(f"Error al obtener el historial general de ventas: {e}")
        return "Error interno", 500



@historial_bp.route('/historial_cliente/<int:cliente_id>')
def historial_cliente(cliente_id):
    estado = request.args.get('estado', 'todas')  # Por defecto, 'todas'

    try:
        # Obtener el nombre del cliente
        cliente_query = "SELECT nombre FROM clientes WHERE id = %s"
        connection = connection_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(cliente_query, (cliente_id,))
        cliente = cursor.fetchone()
        cursor.close()
        
        if not cliente:
            if 'connection' in locals():
                connection_pool.putconn(connection)
            raise ValueError("Cliente no encontrado")
        
        # Filtrar ventas según el estado
        ventas = HistorialModel.obtener_ventas_por_cliente(cliente_id, estado)
        
        if 'connection' in locals():
            connection_pool.putconn(connection)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'data': ventas})
        
        # Pasar el nombre del cliente a la plantilla
        return render_template('ventas/historial_cliente.html', ventas=ventas, cliente_id=cliente_id, cliente_nombre=cliente['nombre'])
    
    except Exception as e:
        error_message = f"Error al obtener las ventas del cliente {cliente_id}: {str(e)}"
        print(error_message)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': error_message}), 500
        return "Error interno", 500
