from app.db import connection_pool as db

class FacturaFabricacion:
    def __init__(self, id, numero_factura, id_proveedor, fecha, total, nombre_proveedor=None):
        self.id = id
        self.numero_factura = numero_factura
        self.id_proveedor = id_proveedor
        self.fecha = fecha
        self.total = total
        self.nombre_proveedor = nombre_proveedor



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
        # Construcción de la consulta base con JOIN
        query = """
            SELECT f.*, p.nombre AS nombre_proveedor 
            FROM facturas_fabricacion f
            JOIN proveedores p ON f.id_proveedor = p.id
            WHERE 1=1
        """
        
        # Aplicar filtros si están presentes
        if fecha:
            query += f" AND DATE(f.fecha) = '{fecha}'"
        if mes:
            query += f" AND DATE_FORMAT(f.fecha, '%Y-%m') = '{mes}'"
        if anio:
            query += f" AND YEAR(f.fecha) = '{anio}'"

        query += " ORDER BY f.id DESC"  # Ordenar por ID de forma descendente
        
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


    @staticmethod
    def actualizar_factura(numero_factura, id_proveedor, total, id):
        try:
            query = """
            UPDATE facturas_fabricacion
            SET numero_factura = %s, id_proveedor = %s, total = %s
            WHERE id = %s
            """
            connection = db.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, (numero_factura,id_proveedor, total, id))
                connection.commit()
            connection.close()
        
        except Exception as e:
            print(f'Error {e}')
            
            
    @staticmethod
    def obtener_factura_por_id(id):
        try:
            query = """
            SELECT * FROM facturas_fabricacion 
            WHERE id = %s
            """
            connection = db.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (id,))
                factura = cursor.fetchone()
            connection.close()
            return factura
        
        except Exception as e:
            print(f'Error {e}')
            return None