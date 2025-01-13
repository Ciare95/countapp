from app.db import connection_pool as db

class FacturaFabricacion:
    def __init__(self, id, numero_factura, proveedor_id, fecha, total):
        self.id = id
        self.numero_factura = numero_factura
        self.proveedor_id = proveedor_id
        self.fecha = fecha
        self.total = total

    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM facturas_fabricacion"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()
        return [FacturaFabricacion(**r) for r in resultados]

    @staticmethod
    def crear(numero_factura, proveedor_id, fecha, total):
        query = """
        INSERT INTO facturas_fabricacion (numero_factura, proveedor_id, fecha, total)
        VALUES (%s, %s, %s, %s)
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (numero_factura, proveedor_id, fecha, total))
            connection.commit()
        connection.close()
