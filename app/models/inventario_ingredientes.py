from app.db import connection_pool as db

class InventarioIngrediente:
    def __init__(self, id, ingrediente_id, cantidad):
        self.id = id
        self.ingrediente_id = ingrediente_id
        self.cantidad = cantidad

    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM inventario_ingredientes"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()
        return [InventarioIngrediente(**r) for r in resultados]

    @staticmethod
    def actualizar_cantidad(ingrediente_id, cantidad):
        query = """
        UPDATE inventario_ingredientes
        SET cantidad = %s
        WHERE ingrediente_id = %s
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (cantidad, ingrediente_id))
            connection.commit()
        connection.close()
