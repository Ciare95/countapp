from app.db import connection_pool

class ProveedorModel:
    @staticmethod
    def obtener_proveedores():
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = "SELECT id, nombre, nit, telefono FROM proveedores"
            cursor.execute(query)
            proveedores = cursor.fetchall()
            return [{'id': p[0], 'nombre': p[1], 'nit': p[2], 'telefono': p[3]} for p in proveedores]
        finally:
            if cursor:
                cursor.close()
            connection.close()

    @staticmethod
    def crear_proveedor(nombre, nit, telefono):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = "INSERT INTO proveedores (nombre, nit, telefono) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, nit, telefono))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error al crear proveedor: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            connection.close()

    @staticmethod
    def actualizar_proveedor(id, nombre, nit, telefono):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = "UPDATE proveedores SET nombre = %s, nit = %s, telefono = %s WHERE id = %s"
            cursor.execute(query, (nombre, nit, telefono, id))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            connection.close()

    @staticmethod
    def eliminar_proveedor(id):
        connection = connection_pool.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = "DELETE FROM proveedores WHERE id = %s"
            cursor.execute(query, (id,))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar proveedor: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            connection.close()