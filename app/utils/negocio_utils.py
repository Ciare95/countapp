from flask_login import current_user

def obtener_id_negocio_actual():
    """
    Obtiene el ID del negocio del usuario actualmente autenticado.
    Para superadmin (rol 1), puede retornar None para acceder a todos los negocios.
    """
    if not current_user.is_authenticated:
        return None
    
    # Superadmin puede ver todos los negocios (retorna None para no filtrar)
    if current_user.id_rol == 1:  # superadmin
        return None
    
    # Usuarios normales solo pueden acceder a su propio negocio
    return current_user.id_negocio

def es_superadmin():
    """Verifica si el usuario actual es superadmin"""
    return current_user.is_authenticated and current_user.id_rol == 1

def tiene_acceso_negocio(id_negocio_solicitado):
    """
    Verifica si el usuario actual tiene acceso al negocio solicitado.
    Superadmin tiene acceso a todos los negocios.
    Usuarios normales solo tienen acceso a su propio negocio.
    """
    if not current_user.is_authenticated:
        return False
    
    if current_user.id_rol == 1:  # superadmin
        return True
    
    return current_user.id_negocio == id_negocio_solicitado
