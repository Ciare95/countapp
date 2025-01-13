from app.db import connection_pool as db

class ProductoFabricado:
    def __init__(self, id, nombre, unidad_medida, costo_total, precio_venta, cantidad_producida, ganancia_neta, porcentaje_rentabilidad):
        self.id = id
        self.nombre = nombre
        self.unidad_medida = unidad_medida
        self.costo_total = costo_total
        self.precio_venta = precio_venta
        self.cantidad_producida = cantidad_producida
        self.ganancia_neta = ganancia_neta
        self.porcentaje_rentabilidad = porcentaje_rentabilidad

    @staticmethod
    def formato_peso_colombiano(valor):
        if valor is None:
            return "0"
        return f"{'{:,.0f}'.format(float(valor)).replace(',', '.')}"

    def precio_venta_formateado(self):
        return self.formato_peso_colombiano(self.precio_venta)

    def costo_total_formateado(self):
        return self.formato_peso_colombiano(self.costo_total)
    

    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM productos_fabricados"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()

        # Calcular ganancia neta y porcentaje de rentabilidad
        productos = []
        for r in resultados:
            ganancia_neta = (r['precio_venta'] - r['costo_total']) if r['costo_total'] is not None else 0
            porcentaje_rentabilidad = (ganancia_neta * 100 / r['precio_venta']) if r['precio_venta'] > 0 else 0

            producto = ProductoFabricado(
                id=r['id'],
                nombre=r['nombre'],
                unidad_medida=r['unidad_medida'],
                costo_total=r['costo_total'],
                precio_venta=r['precio_venta'],
                cantidad_producida=r['cantidad_producida'],
                ganancia_neta=ganancia_neta,
                porcentaje_rentabilidad=porcentaje_rentabilidad
            )
            productos.append(producto)

        return productos


    @staticmethod
    def obtener_por_id(producto_id):
        query = "SELECT * FROM productos_fabricados WHERE id = %s"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, (producto_id,))
            resultado = cursor.fetchone()
        connection.close()
        return ProductoFabricado(**resultado) if resultado else None


    @staticmethod
    def crear(nombre, unidad_medida, costo_total, precio_venta, cantidad_producida):
        query = """
            INSERT INTO productos_fabricados (nombre, unidad_medida, costo_total, precio_venta, cantidad_producida)
            VALUES (%s, %s, %s, %s, %s)
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (nombre, unidad_medida, costo_total, precio_venta, cantidad_producida))
            connection.commit()
        connection.close()


    @staticmethod
    def actualizar(producto_id, nombre, unidad_medida, cantidad_producida, precio_venta):
        query = """
        UPDATE productos_fabricados
        SET nombre = %s, unidad_medida = %s, cantidad_producida = %s, precio_venta = %s
        WHERE id = %s
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (nombre, unidad_medida, cantidad_producida, precio_venta, producto_id))
            connection.commit()
        connection.close()

    @staticmethod
    def eliminar(producto_id):
        query = "DELETE FROM productos_fabricados WHERE id = %s"
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (producto_id,))
            connection.commit()
        connection.close()

    
    def obtener_ingredientes(self):
        query = """
            SELECT 
                i.nombre,
                ip.costo_factura,
                ip.costo_ing_por_producto,
                ip.unidad_medida,
                ip.cantidad_ing,
                ip.cantidad_factura,
                i.id as ingrediente_id,
                ip.costo_empaque
            FROM ingredientes_producto ip
            JOIN ingredientes i ON ip.ingrediente_id = i.id
            WHERE ip.producto_id = %s
        """
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, (self.id,))
            resultados = cursor.fetchall()
        connection.close()
        
        
        return resultados
    
    
    @staticmethod
    def actualizar_costo_total(producto_id, costo_total):
        query = "UPDATE productos_fabricados SET costo_total = %s WHERE id = %s"
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (costo_total, producto_id))
            connection.commit()
        connection.close()