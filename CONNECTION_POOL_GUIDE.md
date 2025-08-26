# Guía de Manejo de Pool de Conexiones

## Problema Resuelto: "connection pool exhausted"

El error `psycopg2.pool.PoolError: connection pool exhausted` ocurría porque:

1. **Configuración inadecuada**: El pool tenía solo 15 conexiones máximas
2. **Doble inicialización**: `initialize_schema()` se llamaba dos veces
3. **Manejo de errores deficiente**: Las conexiones no siempre se devolvían al pool
4. **Fugas de conexiones**: Excepciones prevenían que las conexiones se liberaran

## Soluciones Implementadas

### 1. Configuración Optimizada del Pool

En `app/db.py`:
```python
connection_pool = pool.SimpleConnectionPool(
    2,                    # minconn (aumentado para producción)
    30,                   # maxconn (aumentado significativamente)
    conn_string,
    timeout=30            # timeout de 30 segundos
)
```

### 2. Corrección de Doble Inicialización

Eliminada la llamada duplicada a `initialize_schema()` en `run.py`.

### 3. Mejor Manejo de Errores

Implementado en `app/__init__.py` para las funciones `load_user` e `index`:
- Variables inicializadas como `None`
- Bloques `try/finally` robustos
- Manejo de excepciones en cada operación de cierre

### 4. Utilidades para Manejo Seguro

Creado `app/db_utils.py` con context managers:
- `get_db_connection()`: Para obtener conexiones de manera segura
- `get_db_cursor()`: Para operaciones con commit/rollback automático
- Funciones helper para consultas comunes

## Uso Recomendado

### Para nuevas funciones:

```python
from app.db_utils import get_db_cursor

def mi_funcion():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM tabla")
        resultados = cursor.fetchall()
    # La conexión se libera automáticamente
```

### Para migrar funciones existentes:

Reemplazar este patrón:
```python
conexion = connection_pool.getconn()
cursor = None
try:
    cursor = conexion.cursor()
    # operaciones...
finally:
    if cursor:
        cursor.close()
    if 'conexion' in locals():
        connection_pool.putconn(conexion)
```

Con:
```python
with get_db_cursor() as cursor:
    # operaciones...
```

## Herramientas de Monitoreo

### 1. Test de Pool
```bash
python test_connection_pool.py
```

### 2. Monitor en Tiempo Real
```bash
python monitor_pool.py monitor
```

### 3. Verificación de Salud
```bash
python monitor_pool.py
```

## Configuración para Diferentes Entornos

### Desarrollo Local:
- `minconn`: 2
- `maxconn`: 10-15
- `timeout`: 30 segundos

### Producción (Render/Heroku):
- `minconn`: 2-5  
- `maxconn`: 20-30
- `timeout`: 30 segundos

## Mejores Prácticas

1. **Siempre usar context managers** (`with get_db_cursor() as cursor:`)
2. **Manejar excepciones adecuadamente** pero no silenciar errores críticos
3. **Liberar conexiones inmediatamente** después de usarlas
4. **Evitar mantener conexiones abiertas** por largos períodos
5. **Monitorear regularmente** el estado del pool en producción

## Troubleshooting

### Síntomas de Pool Agotado:
- Errores "connection pool exhausted"
- Lentitud en las respuestas
- Timeouts en operaciones de base de datos

### Soluciones:
1. Verificar que todas las conexiones se liberen
2. Aumentar `maxconn` si es necesario
3. Revisar consultas lentas que mantengan conexiones ocupadas
4. Usar los scripts de monitoreo para diagnosticar

## Notas de Render.com

- Las bases de datos en Render tienen límites de conexiones
- El plan gratuito generalmente permite 20 conexiones máximas
- Ajustar `maxconn` según el plan de base de datos
- Considerar usar `timeout` para evitar bloqueos indefinidos
