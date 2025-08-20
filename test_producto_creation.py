#!/usr/bin/env python3
"""
Script para probar la creación de productos y verificar si hay errores
"""

import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import connection_pool
from app.models.productos import Producto

def test_crear_producto():
    """Prueba la creación de un producto"""
    try:
        # Crear un producto de prueba
        producto = Producto()
        producto.nombre = "Producto de Prueba"
        producto.id_categorias = 1  # Asumiendo que existe una categoría con ID 1
        producto.precio = 10000
        producto.precio_compra = 5000
        producto.cantidad = 10
        producto.es_servicio = False
        
        print("Intentando crear producto...")
        resultado = producto.crear_producto()
        
        if resultado:
            print("✅ Producto creado exitosamente!")
            return True
        else:
            print("❌ Error al crear el producto")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al crear producto: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Prueba de creación de producto ===")
    success = test_crear_producto()
    if success:
        print("\n✅ Prueba exitosa! El problema podría estar en el entorno de Render.")
    else:
        print("\n❌ Prueba fallida. Revisar la configuración local.")
