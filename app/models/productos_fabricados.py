from app.db import connection_pool as db

class ProductoFabricado:
    def __init__(self, id, nombre, unidad_medida, costo_total, precio_venta, cantidad_producida):
        self.id = id
        self.nombre = nombre
        self.unidad_medida = unidad_medida
        self.costo_total = costo_total
        self.precio_venta = precio_venta
        self.cantidad_producida = cantidad_producida

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
        return [ProductoFabricado(**r) for r in resultados]

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