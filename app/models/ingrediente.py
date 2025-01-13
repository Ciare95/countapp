from app.db import connection_pool as db

class Ingrediente:
    def __init__(self, id, nombre, descripcion, costo_factura=None, costo_unitario=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.costo_unitario = costo_unitario
        self.costo_factura = costo_factura



    @staticmethod
    def crear(nombre, descripcion):
        query = """
        INSERT INTO ingredientes (nombre, descripcion)
        VALUES (%s, %s)
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (nombre, descripcion))
            connection.commit()
        connection.close()


    @staticmethod
    def actualizar(id, nombre, descripcion):
        query = """
        UPDATE ingredientes
        SET nombre = %s, descripcion = %s
        WHERE id = %s
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (nombre, descripcion, id))
            connection.commit()
        connection.close()

    

    @staticmethod
    def eliminar(id):
        query = "DELETE FROM ingredientes WHERE id = %s"
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (id,))
            connection.commit()
        connection.close()
        

    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM ingredientes"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()
        return [Ingrediente(**r) for r in resultados]
    
    
    @staticmethod
    def obtener_por_id(id):
        query = "SELECT * FROM ingredientes WHERE id = %s"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, (id,))
            resultado = cursor.fetchone()
        connection.close()
        if resultado:
            return Ingrediente(**resultado)
        return None
    
    @staticmethod
    def guardar_ingrediente(datos):
        # Verificar si ya existe el ingrediente para este producto
        query_verificar = """
        SELECT id FROM ingredientes_producto
        WHERE producto_id = %s AND ingrediente_id = %s
        """
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query_verificar, (datos['producto_id'], datos['ingrediente_id']))
            existente = cursor.fetchone()

        # Si existe, actualizar los datos
        if existente:
            query_actualizar = """
            UPDATE ingredientes_producto
            SET costo_factura = %s,
                costo_ing_por_producto = %s,
                unidad_medida = %s,
                cantidad_ing = %s,
                cantidad_factura = %s
            WHERE producto_id = %s AND ingrediente_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query_actualizar, (
                    datos['costo_factura'],
                    datos['costo_ing_por_producto'],
                    datos['unidad_medida'],
                    datos['cantidad_ing'],
                    datos['cantidad_factura'],
                    datos['producto_id'],
                    datos['ingrediente_id']
                ))
            connection.commit()
        # Si no existe, insertar un nuevo registro
        else:
            query_insertar = """
            INSERT INTO ingredientes_producto
            (producto_id, ingrediente_id, costo_factura, costo_ing_por_producto, unidad_medida, cantidad_ing, cantidad_factura)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(query_insertar, (
                    datos['producto_id'],
                    datos['ingrediente_id'],
                    datos['costo_factura'],
                    datos['costo_ing_por_producto'],
                    datos['unidad_medida'],
                    datos['cantidad_ing'],
                    datos['cantidad_factura']
                ))
            connection.commit()

        connection.close()

    @staticmethod
    def obtener_costo_total(producto_id):
        query = """
        SELECT SUM(costo_ing_por_producto) AS costo_total
        FROM ingredientes_producto
        WHERE producto_id = %s
        """
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, (producto_id,))
            resultado = cursor.fetchone()
        connection.close()
        return resultado['costo_total'] if resultado else 0