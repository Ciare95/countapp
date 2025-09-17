#!/usr/bin/env python3
"""
Script para configurar variables de entorno fácilmente
"""

import os
import sys

def setup_environment():
    """Configurar variables de entorno"""
    print("=== CONFIGURACIÓN DE VARIABLES DE ENTORNO ===")
    
    # Verificar si ya existe un archivo .env
    if os.path.exists('.env'):
        print("⚠️  Ya existe un archivo .env. ¿Quieres sobrescribirlo? (s/n)")
        respuesta = input().strip().lower()
        if respuesta != 's':
            print("Configuración cancelada.")
            return
    
    # Solicitar información de configuración
    print("\nPor favor, ingresa la información de tu base de datos PostgreSQL:")
    
    db_host = input("Host (default: localhost): ").strip() or "localhost"
    db_user = input("Usuario (default: postgres): ").strip() or "postgres"
    db_password = input("Password: ").strip()
    db_database = input("Base de datos (default: sistema_papeleria): ").strip() or "sistema_papeleria"
    db_port = input("Puerto (default: 5432): ").strip() or "5432"
    
    # Crear contenido del archivo .env
    env_content = f"""# Configuración de Base de Datos para Desarrollo Local
DB_HOST={db_host}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_DATABASE={db_database}
DB_PORT={db_port}

# Configuración para Render/Heroku (se usa DATABASE_URL automáticamente)
# DATABASE_URL=postgresql://usuario:password@host:port/database

# Clave secreta para Flask
FLASK_SECRET_KEY=tu_clave_secreta_aqui_cambiar_por_una_segura
"""
    
    # Escribir archivo .env
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Archivo .env creado exitosamente!")
        print("📋 Recuerda:")
        print("   - El archivo .env NO debe subirse a Git (está en .gitignore)")
        print("   - Para producción, configura las variables en tu hosting (Render/Heroku)")
        print("   - Ejecuta: 'source .env' o reinicia tu terminal para cargar las variables")
        
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")

def load_env_file():
    """Cargar variables desde archivo .env"""
    if os.path.exists('.env'):
        print("Cargando variables desde .env...")
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("Variables cargadas correctamente.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'load':
        load_env_file()
    else:
        setup_environment()
