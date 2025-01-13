from app.db import connection_pool
from mysql.connector import Error
from datetime import datetime

class HistorialModel:
    @staticmethod
    def formato_peso_colombiano(valor):
        if valor is None:
            return "0"
        return f"{'{:,.0f}'.format(float(valor)).replace(',', '.')}"
    

    @staticmethod
    def obtener_ventas_generales(where_clause="", parametros=None):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            # Query para obtener ventas individuales, incluyendo el nombre del usuario
            query_ventas = f"""
                SELECT v.id AS id_venta, v.fecha_venta, 
                    SUM(dv.cantidad * p.precio) AS total_venta, 
                    v.estado, v.saldo, c.nombre AS cliente,
                    u.nombre AS usuario
                FROM ventas v
                JOIN detalle_ventas dv ON v.id = dv.id_ventas
                JOIN productos p ON dv.id_productos = p.id
                JOIN clientes c ON v.id_cliente = c.id
                LEFT JOIN usuarios u ON v.id_usuarios = u.id
                {where_clause}
                GROUP BY v.id, v.fecha_venta, v.estado, v.saldo, c.nombre, u.nombre
                ORDER BY v.fecha_venta DESC
            """
            
            # Query para obtener totales
            query_totales = f"""
                SELECT 
                    COALESCE(SUM(total_venta), 0) as total_ventas,
                    COALESCE(SUM(saldo), 0) as total_saldos
                FROM (
                    SELECT v.id, SUM(dv.cantidad * p.precio) as total_venta, v.saldo
                    FROM ventas v
                    JOIN detalle_ventas dv ON v.id = dv.id_ventas
                    JOIN productos p ON dv.id_productos = p.id
                    {where_clause}
                    GROUP BY v.id, v.saldo
                ) as subtotales
            """
            
            # Ejecutar queries
            cursor.execute(query_ventas, parametros or {})
            resultados = cursor.fetchall()
            
            cursor.execute(query_totales, parametros or {})
            totales = cursor.fetchone()
            
            # Formatear resultados
            for resultado in resultados:
                resultado['total_venta'] = HistorialModel.formato_peso_colombiano(resultado['total_venta'])
                resultado['saldo'] = HistorialModel.formato_peso_colombiano(resultado['saldo'])
                fecha = datetime.strptime(str(resultado['fecha_venta']), '%Y-%m-%d %H:%M:%S')
                resultado['fecha_venta'] = fecha.strftime('%Y-%m-%d %H:%M')
            
            total_ventas = totales.get('total_ventas', 0) or 0
            total_saldos = totales.get('total_saldos', 0) or 0
            total_neto = total_ventas - total_saldos

            
            # Formatear totales
            totales_formateados = {
                'total_ventas': HistorialModel.formato_peso_colombiano(total_ventas),
                'total_saldos': HistorialModel.formato_peso_colombiano(total_saldos),
                'total_neto': HistorialModel.formato_peso_colombiano(total_neto)
            }

            
            
            return resultados, totales_formateados
        finally:
            if cursor:
                cursor.close()
            connection.close()

            
    @staticmethod
    def obtener_ventas_por_cliente(cliente_id, estado='todas'):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Construir la consulta base con JOIN para obtener el nombre del vendedor
            query = """
                SELECT v.id AS id_venta, v.fecha_venta, 
                    SUM(dv.cantidad * p.precio) AS total_venta, 
                    v.estado, v.saldo, u.nombre AS usuario
                FROM ventas v
                JOIN detalle_ventas dv ON v.id = dv.id_ventas
                JOIN productos p ON dv.id_productos = p.id
                JOIN usuarios u ON v.id_usuarios = u.id  -- Unir con la tabla usuarios para obtener el nombre
                WHERE v.id_cliente = %s
            """
            
            # Filtrar por estado si se proporciona
            if estado != 'todas':
                query += " AND v.estado = %s"
            
            # Ordenar por fecha
            query += " GROUP BY v.id ORDER BY v.fecha_venta DESC"
            
            # Ejecutar la consulta
            if estado != 'todas':
                cursor.execute(query, (cliente_id, estado))
            else:
                cursor.execute(query, (cliente_id,))
            
            ventas = cursor.fetchall()
            
            # Obtener detalles de cada venta
            for venta in ventas:
                details_query = """
                    SELECT p.nombre AS producto, dv.cantidad, 
                        p.precio, (dv.cantidad * p.precio) AS subtotal
                    FROM detalle_ventas dv
                    JOIN productos p ON dv.id_productos = p.id
                    WHERE dv.id_ventas = %s
                """
                cursor.execute(details_query, (venta['id_venta'],))
                detalles = cursor.fetchall()
                
                # Formatear valores monetarios en detalles
                for detalle in detalles:
                    detalle['precio'] = HistorialModel.formato_peso_colombiano(detalle['precio'])
                    detalle['subtotal'] = HistorialModel.formato_peso_colombiano(detalle['subtotal'])
                
                venta['detalles'] = detalles
                venta['total_venta'] = HistorialModel.formato_peso_colombiano(venta['total_venta'])
                venta['saldo'] = HistorialModel.formato_peso_colombiano(venta['saldo'])
            
            return ventas
        finally:
            if cursor:
                cursor.close()
            connection.close()

