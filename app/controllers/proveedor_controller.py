from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from app.models.proveedor import ProveedorModel

proveedor_bp = Blueprint('proveedor', __name__)

# JSON API route
@proveedor_bp.route('/api', methods=['GET'])
def obtener_proveedores():
    try:
        proveedores = ProveedorModel.obtener_proveedores()
        return jsonify(proveedores), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error al obtener los proveedores'}), 500
    

@proveedor_bp.route('/listar', methods=['GET'])
def listar_proveedores():
    try:
        proveedores = ProveedorModel.obtener_proveedores()
        return render_template('proveedores/listar.html', proveedores=proveedores)
    except Exception as e:
        print(f"Error: {e}")
        flash("Error al obtener los proveedores. Inténtalo nuevamente.", "danger")
        return render_template('proveedores/listar.html', proveedores=[])


@proveedor_bp.route('/crear', methods=['POST'])
def crear_proveedor():
    try:
        data = request.json  #Recibe en formato json
        nombre = data.get('nombre')
        nit = data.get('nit')
        telefono = data.get('telefono')
        if ProveedorModel.crear_proveedor(nombre, nit, telefono):
            flash("Proveedor creado exitosamente.", "success")
            return redirect(url_for('proveedor.listar_proveedores'))
        flash("Error al crear el proveedor.", "danger")
        return redirect(url_for('proveedor.listar_proveedores'))
    except Exception as e:
        print(f"Error: {e}")
        flash("Error al crear el proveedor. Inténtalo nuevamente.", "danger")
        return redirect(url_for('proveedor.listar_proveedores'))


@proveedor_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar_proveedor(id):
    try:
        data = request.json  # Cambiado a `request.json` para JSON
        nombre = data.get('nombre')
        nit = data.get('nit')
        telefono = data.get('telefono')

        if not nombre:  # Validación adicional en el backend
            flash("El campo 'Nombre' es obligatorio.", "danger")
            return redirect(url_for('proveedor.listar_proveedores'))

        if ProveedorModel.actualizar_proveedor(id, nombre, nit, telefono):
            flash("Proveedor actualizado exitosamente.", "success")
            return redirect(url_for('proveedor.listar_proveedores'))

        flash("Error al actualizar el proveedor.", "danger")
        return redirect(url_for('proveedor.listar_proveedores'))
    except Exception as e:
        print(f"Error: {e}")
        flash("Error al actualizar el proveedor. Inténtalo nuevamente.", "danger")
        return redirect(url_for('proveedor.listar_proveedores'))


@proveedor_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_proveedor(id):
    try:
        resultado, mensaje = ProveedorModel.eliminar_proveedor(id)
        if resultado:
            return jsonify({"success": True, "message": "Proveedor eliminado exitosamente."}), 200
        else:
            return jsonify({"success": False, "message": mensaje}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Error al eliminar el proveedor. Inténtalo nuevamente."}), 500

