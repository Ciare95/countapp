from app import create_app  # Importa la función create_app desde app/__init__.py

# Crea la instancia de la aplicación Flask
app = create_app()

# Ejecuta la aplicación 
if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)