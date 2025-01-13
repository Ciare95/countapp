from app.db import connection_pool

class InformeModel:
    
    @staticmethod
    def formato_peso_colombiano(valor):
        if valor is None:
            return "0"
        return f"{'{:,.0f}'.format(float(valor)).replace(',', '.')}"
    
    @staticmethod
    def obtener_ingresos(where_clause="", parametros=None):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            query = f"""
                SELECT 
                    SUM(dv.cantidad * p.precio) - SUM(v.saldo) AS total_ingresos
                FROM detalle_ventas dv
                JOIN productos p ON dv.id_productos = p.id
                JOIN ventas v ON dv.id_ventas = v.id
                {where_clause}
            """
            cursor.execute(query, parametros or {})
            resultado = cursor.fetchone()
            
            if resultado and resultado['total_ingresos'] is not None:
                total_ingresos = float(resultado['total_ingresos'])
                return InformeModel.formato_peso_colombiano(total_ingresos)
            else:
                return InformeModel.formato_peso_colombiano(0.0)

        finally:
            if cursor:
                cursor.close()
            connection.close()


    @staticmethod
    def obtener_egresos(where_clause="", parametros=None):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # 1. Egresos de productos
            query_productos = f"""
                SELECT COALESCE(SUM(dv.cantidad * p.precio_compra), 0) AS egresos_productos
                FROM detalle_ventas dv
                JOIN productos p ON dv.id_productos = p.id
                JOIN ventas v ON dv.id_ventas = v.id
                {where_clause}
            """
            cursor.execute(query_productos, parametros or {})
            resultado_productos = cursor.fetchone()
            egresos_productos = float(resultado_productos['egresos_productos']) if resultado_productos['egresos_productos'] else 0.0

            # 2. Egresos de facturas
            where_facturas = where_clause.replace('v.fecha_venta', 'fecha_factura') if where_clause else ""
            query_facturas = f"""
                SELECT COALESCE(SUM(total), 0) AS egresos_facturas
                FROM facturas
                {where_facturas}
            """
            cursor.execute(query_facturas, parametros or {})
            resultado_facturas = cursor.fetchone()
            egresos_facturas = float(resultado_facturas['egresos_facturas']) if resultado_facturas['egresos_facturas'] else 0.0

            # 3. Otros egresos
            where_otros = where_clause.replace('v.fecha_venta', 'fecha') if where_clause else ""
            query_otros = f"""
                SELECT COALESCE(SUM(valor), 0) AS otros_egresos
                FROM otros_egresos
                {where_otros}
            """
            cursor.execute(query_otros, parametros or {})
            resultado_otros = cursor.fetchone()
            otros_egresos = float(resultado_otros['otros_egresos']) if resultado_otros['otros_egresos'] else 0.0

            # Sumamos todos los egresos
            total_egresos = egresos_productos + egresos_facturas + otros_egresos
            return InformeModel.formato_peso_colombiano(total_egresos)

        finally:
            if cursor:
                cursor.close()
            connection.close()

    @staticmethod
    def registrar_otro_egreso(descripcion, valor):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = "INSERT INTO otros_egresos (descripcion, valor) VALUES (%s, %s)"
            cursor.execute(query, (descripcion, valor))
            connection.commit()
        finally:
            if cursor:
                cursor.close()
            connection.close()


    @staticmethod
    def listar_otros_egresos():
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM otros_egresos"
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Formatea el valor de cada resultado
            for resultado in resultados:
                if resultado and resultado['valor'] is not None:
                    resultado['valor_formato'] = InformeModel.formato_peso_colombiano(resultado['valor'])
                else:
                    resultado['valor_formato'] = InformeModel.formato_peso_colombiano(0.0)
            
            return resultados
            
        finally:
            if cursor:
                cursor.close()
            connection.close()

        
