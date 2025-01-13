from app.db import connection_pool as db

class IngredienteFactura:
    def __init__(self, id, nombre, cantidad, costo_unitario, factura_id):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.costo_unitario = costo_unitario
        self.factura_id = factura_id

    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM ingredientes_factura"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()
        return [IngredienteFactura(**r) for r in resultados]

    @staticmethod
    def crear(nombre, cantidad, costo_unitario, factura_id):
        query = """
        INSERT INTO ingredientes_factura (nombre, cantidad, costo_unitario, factura_id)
        VALUES (%s, %s, %s, %s)
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (nombre, cantidad, costo_unitario, factura_id))
            connection.commit()
        connection.close()
