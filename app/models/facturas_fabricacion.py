from app.db import connection_pool as db

class FacturaFabricacion:
    def __init__(self, id, numero_factura, id_proveedor, fecha, total):
        self.id = id
        self.numero_factura = numero_factura
        self.id_proveedor = id_proveedor
        self.fecha = fecha
        self.total = total

    @staticmethod
    def obtener_todos():
        query = "SELECT * FROM facturas_fabricacion ORDER BY id DESC"
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()
        return [FacturaFabricacion(**r) for r in resultados]

    @staticmethod
    def obtener_con_filtros(fecha=None, mes=None, anio=None):
        # Construcción de la consulta base
        query = "SELECT * FROM facturas_fabricacion WHERE 1=1"
        
        # Aplicar filtros si están presentes
        if fecha:
            query += f" AND DATE(fecha) = '{fecha}'"
        if mes:
            query += f" AND DATE_FORMAT(fecha, '%Y-%m') = '{mes}'"
        if anio:
            query += f" AND YEAR(fecha) = '{anio}'"

        query += " ORDER BY id DESC"  # Ordenar por ID de forma descendente
        
        connection = db.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        connection.close()

        return [FacturaFabricacion(**r) for r in resultados]

    @staticmethod
    def crear(numero_factura, id_proveedor, fecha, total):
        query = """
        INSERT INTO facturas_fabricacion (numero_factura, id_proveedor, fecha, total)
        VALUES (%s, %s, %s, %s)
        """
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (numero_factura, id_proveedor, fecha, total))
            connection.commit()
        connection.close()
