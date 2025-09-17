#!/usr/bin/env python3
"""
Script para automatizar la modificación de controladores para soporte multi-negocio
"""

import os
import re
from pathlib import Path

# Directorio de controladores
CONTROLLERS_DIR = Path("app/controllers")

# Patrones para buscar y modificar
PATTERNS = {
    'imports': [
        (r'from flask_login import.*', r'from flask_login import login_required, current_user'),
        (r'from flask_login import login_required', r'from flask_login import login_required, current_user'),
    ],
    'new_imports': [
        'from app.utils.negocio_utils import obtener_id_negocio_actual, tiene_acceso_negocio'
    ],
    'function_patterns': [
        # Patrones para métodos que obtienen datos
        (r'def (.*)\(.*\):\s*\n\s*.*\.obtener_', 
         r'def \1():\n    id_negocio = obtener_id_negocio_actual()\n    .obtener_'),
        
        # Patrones para métodos que crean datos
        (r'def (.*)\(.*\):\s*\n\s*.*\.crear_', 
         r'def \1():\n    id_negocio = obtener_id_negocio_actual()\n    .crear_'),
        
        # Patrones para métodos que editan datos
        (r'def (.*)\(.*\):\s*\n\s*.*\.editar_', 
         r'def \1():\n    id_negocio = obtener_id_negocio_actual()\n    .editar_'),
        
        # Patrones para métodos que eliminan datos
        (r'def (.*)\(.*\):\s*\n\s*.*\.eliminar_', 
         r'def \1():\n    id_negocio = obtener_id_negocio_actual()\n    .eliminar_'),
    ]
}

def modify_controller(file_path):
    """Modifica un controlador para agregar soporte multi-negocio"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Agregar imports necesarios
        if 'from app.utils.negocio_utils import' not in content:
            # Encontrar la última línea de import
            import_lines = []
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    import_lines.append(i)
            
            if import_lines:
                last_import_line = max(import_lines)
                lines.insert(last_import_line + 1, 'from app.utils.negocio_utils import obtener_id_negocio_actual, tiene_acceso_negocio')
                content = '\n'.join(lines)
        
        # Agregar login_required a métodos que no lo tengan
        routes_without_login = re.findall(r'@.*route.*\n(?!.*@login_required.*\n)def (listar|obtener|crear|editar|eliminar)', content)
        if routes_without_login:
            content = re.sub(
                r'(@.*route.*\n)(def (listar|obtener|crear|editar|eliminar))',
                r'\1@login_required\n\2',
                content
            )
        
        # Modificar métodos para usar id_negocio
        content = re.sub(
            r'def (listar|obtener)_(.*)\(.*\):\s*\n\s*(.*)\.obtener_',
            r'def \1_\2():\n    id_negocio = obtener_id_negocio_actual()\n    \3.obtener_',
            content
        )
        
        content = re.sub(
            r'def crear_(.*)\(.*\):\s*\n\s*(.*)\.crear_',
            r'def crear_\1():\n    id_negocio = obtener_id_negocio_actual()\n    \2.crear_',
            content
        )
        
        content = re.sub(
            r'def editar_(.*)\(.*\):\s*\n\s*(.*)\.editar_',
            r'def editar_\1():\n    id_negocio = obtener_id_negocio_actual()\n    \2.editar_',
            content
        )
        
        content = re.sub(
            r'def eliminar_(.*)\(.*\):\s*\n\s*(.*)\.eliminar_',
            r'def eliminar_\1():\n    id_negocio = obtener_id_negocio_actual()\n    \2.eliminar_',
            content
        )
        
        # Guardar cambios si hubo modificaciones
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Modificado: {file_path}")
            return True
        else:
            print(f"○ Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("=== MODIFICACIÓN DE CONTROLADORES PARA MULTI-NEGOCIO ===")
    
    modified_count = 0
    total_count = 0
    
    # Procesar todos los archivos de controladores
    for controller_file in CONTROLLERS_DIR.glob("*.py"):
        if controller_file.name != "__init__.py":
            total_count += 1
            if modify_controller(controller_file):
                modified_count += 1
    
    print(f"\nResumen: {modified_count}/{total_count} controladores modificados")
    
    if modified_count > 0:
        print("\n✅ Modificaciones completadas. Ahora necesitas:")
        print("1. Actualizar los modelos correspondientes para aceptar el parámetro id_negocio")
        print("2. Verificar que todas las consultas SQL incluyan filtros por id_negocio")
        print("3. Probar las funcionalidades con diferentes usuarios de diferentes negocios")
    else:
        print("\nℹ️ No se realizaron modificaciones. Los controladores pueden ya estar actualizados.")

if __name__ == "__main__":
    main()
