from app import create_app  # Importa la función create_app desde app/__init__.py

# Crea la instancia de la aplicación Flask (el esquema se inicializa dentro de create_app)
app = create_app()

# Ejecuta la aplicación 
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
