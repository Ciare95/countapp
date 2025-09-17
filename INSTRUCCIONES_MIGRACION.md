# Instrucciones para Migración a Multi-Negocio

## 📋 Pasos para convertir tu aplicación en SaaS multi-negocio

### 1. Preparación del Entorno

Asegúrate de tener:
- Python 3.8+ instalado
- PostgreSQL instalado y funcionando

### 2. Configurar Variables de Entorno

**Para desarrollo local:**
```bash
# Ejecutar el script de configuración
python setup_env.py

# O crear manualmente el archivo .env
cp .env.example .env
# Editar el archivo .env con tus credenciales de PostgreSQL
```

**Las variables necesarias son:**
- `DB_HOST`: localhost (o la IP de tu servidor PostgreSQL)
- `DB_USER`: postgres (o tu usuario de PostgreSQL)
- `DB_PASSWORD`: tu contraseña de PostgreSQL
- `DB_DATABASE`: sistema_papeleria (o el nombre de tu base de datos)
- `DB_PORT`: 5432 (puerto por defecto de PostgreSQL)

### 2. Backup de la Base de Datos (IMPORTANTE)

**ANTES DE CONTINUAR, HAZ UN BACKUP COMPLETO DE TU BASE DE DATOS:**

```bash
# Para PostgreSQL local
pg_dump -h localhost -U postgres sistema_papeleria > backup_pre_migracion.sql

# Para Render/Heroku
heroku pg:backups:capture -a tu-app-name
heroku pg:backups:download -a tu-app-name
```

### 3. Alterar Tablas Existentes

Ejecuta el script para agregar columnas id_negocio a las tablas existentes:

```bash
python alter_existing_tables.py
```

### 4. Migrar Datos Existentes

Ejecuta el script de migración para adaptar los datos existentes:

```bash
python migrate_to_multi_negocio.py
```

**Nota:** El script `apply_new_schema.py` ya no es necesario ya que las tablas ya existen.

### 5. Verificar la Migración

Verifica que la migración se realizó correctamente:

```bash
# Conectarse a la base de datos
psql -h localhost -U postgres -d sistema_papeleria

# Verificar que las tablas tienen la columna id_negocio
\d usuarios
\d productos
\d clientes

# Verificar que los datos se migraron correctamente
SELECT COUNT(*) FROM usuarios WHERE id_negocio IS NOT NULL;
```

### 6. Actualizar la Aplicación

Los cambios realizados hasta ahora:

1. **Modelo de Usuarios actualizado** (`app/models/usuarios.py`):
   - Agregado campo `id_negocio`
   - Métodos actualizados para manejar multi-negocio

2. **Esquema de base de datos** (`schema_multi_negocio.sql`):
   - Todas las tablas principales ahora tienen `id_negocio`
   - Tablas de planes y suscripciones
   - Índices para mejorar rendimiento

3. **Sistema de autenticación** (`app/__init__.py`):
   - `user_loader` actualizado para incluir `id_negocio`

### 7. Próximos Pasos

Después de aplicar la migración, necesitarás:

1. **Modificar todos los controladores** para filtrar por `id_negocio`
2. **Crear interfaz de administración** multi-negocio
3. **Implementar sistema de suscripciones**
4. **Actualizar templates** para mostrar información del negocio
5. **Realizar pruebas exhaustivas**

### 8. Credenciales de Acceso

Después de la migración, tendrás:

- **Usuario superadmin**: `superadmin` / `admin123`
- **Negocio por defecto**: "Mi Negocio" (todos los datos existentes se asociarán a este negocio)

### 9. Consideraciones Importantes

- **No reversible**: La migración modifica la estructura de la base de datos
- **Testing**: Prueba primero en un entorno de desarrollo
- **Render**: Si estás usando Render, necesitarás ejecutar estos scripts en tu instancia de producción después de testing

### 10. Soporte

Si encuentras problemas durante la migración:
1. Verifica que el backup se realizó correctamente
2. Revisa los mensajes de error en la consola
3. Asegúrate de que todas las dependencias estén instaladas

## 🚀 Estado Actual del Proyecto

- [x] Análisis de estructura actual
- [x] Planificación del esquema multi-negocio  
- [x] Implementación de relaciones multi-negocio en modelos
- [ ] Modificación del sistema de autenticación
- [ ] Actualización de consultas para filtrar por negocio
- [ ] Creación de interfaz de administración multi-negocio
- [ ] Implementación de sistema de suscripciones
- [ ] Pruebas de segregación de datos

**¡La migración de base de datos está lista para ser ejecutada!**
