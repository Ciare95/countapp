#!/usr/bin/env python3
"""
Script para automatizar la modificación de modelos para soporte multi-negocio
"""

import os
import re
from pathlib import Path

# Directorio de modelos
MODELS_DIR = Path("app/models")

# Modelos que necesitan ser modificados (excluyendo algunos que ya tienen soporte)
MODELS_TO_MODIFY = [
    "categorias.py",
    "productos.py", 
    "proveedor.py",
    "facturas.py",
    "venta.py",
    "detalle_venta.py",
    "ingrediente.py",
    "productos_fabricados.py",
    "facturas_fabricacion.py",
    "ingredientes_factura.py",
    "ingredientes_productos.py",
    "inventario_ingredientes.py",
    "otros_egresos.py",
    "abonos.py",
    "historial.py",
    "informe.py"
]

def modify_model_methods(content, model_name):
    """Modifica los métodos de un modelo para aceptar id_negocio"""
    
    # Métodos que necesitan ser modificados
    methods_to_modify = [
        ('obtener_por_id', r'def obtener_por_id\(self, id\):', r'def obtener_por_id\(self, id, id_negocio=None\):'),
        ('obtener_todos', r'def obtener_.*\(self\):', r'def obtener_.*\(self, id_negocio=None\):'),
        ('crear', r'def crear_.*\(self\):', r'def crear_.*\(self, id_negocio=None\):'),
        ('actualizar', r'def actualizar_.*\(self\):', r'def actualizar_.*\(self, id_negocio=None\):'),
        ('editar', r'def editar_.*\(self\):', r'def editar_.*\(self, id_negocio=None\):'),
        ('eliminar', r'def eliminar_.*\(self\):', r'def eliminar_.*\(self, id_negocio=None\):')
    ]
    
    modified = False
    
    for method_name, pattern, replacement in methods_to_modify:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"  - Modificado método {method_name}")
    
    return content, modified

def add_id_negocio_to_init(content):
    """Agrega id_negocio al método __init__ si no existe"""
    if 'id_negocio' not in content:
        # Buscar el método __init__
        init_pattern = r'def __init__\(self[^)]*\):'
        match = re.search(init_pattern, content)
        if match:
            # Agregar id_negocio al init
            new_init = match.group(0).replace('):', ', id_negocio=None):')
            content = content.replace(match.group(0), new_init)
            
            # Agregar la asignación de id_negocio
            assignment_pattern = r'self\.id_negocio = id_negocio'
            if assignment_pattern not in content:
                # Encontrar donde asignar las otras variables
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'self.id = id' in line or 'self.nombre = nombre' in line:
                        # Insertar después de la última asignación
                        lines.insert(i + 1, '        self.id_negocio = id_negocio')
                        content = '\n'.join(lines)
                        break
            
            print("  - Agregado id_negocio al __init__")
            return content, True
    
    return content, False

def modify_model(file_path):
    """Modifica un modelo para agregar soporte multi-negocio"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        print(f"\nProcesando: {file_path.name}")
        
        # Agregar id_negocio al __init__
        content, init_modified = add_id_negocio_to_init(content)
        modified = modified or init_modified
        
        # Modificar métodos
        content, methods_modified = modify_model_methods(content, file_path.name)
        modified = modified or methods_modified
        
        # Guardar cambios si hubo modificaciones
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Modificado: {file_path.name}")
            return True
        else:
            print(f"○ Sin cambios: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"✗ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("=== MODIFICACIÓN DE MODELOS PARA MULTI-NEGOCIO ===")
    
    modified_count = 0
    total_count = 0
    
    # Procesar modelos específicos
    for model_file in MODELS_DIR.glob("*.py"):
        if model_file.name in MODELS_TO_MODIFY and model_file.name != "__init__.py":
            total_count += 1
            if modify_model(model_file):
                modified_count += 1
    
    print(f"\nResumen: {modified_count}/{total_count} modelos modificados")
    
    if modified_count > 0:
        print("\n✅ Modificaciones completadas. Ahora necesitas:")
        print("1. Actualizar las consultas SQL en cada modelo para incluir filtros por id_negocio")
        print("2. Verificar que todas las consultas usen el parámetro id_negocio correctamente")
        print("3. Probar las funcionalidades con diferentes usuarios de diferentes negocios")
    else:
        print("\nℹ️ No se realizaron modificaciones. Los modelos pueden ya estar actualizados.")

if __name__ == "__main__":
    main()
