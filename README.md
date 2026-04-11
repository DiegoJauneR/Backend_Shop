# FastAPI Backend Template

Template profesional de backend con FastAPI, autenticación JWT, PostgreSQL y arquitectura escalable.

## 🚀 Características

- ✅ **FastAPI** - Framework moderno y de alto rendimiento
- 🔐 **JWT Authentication** - Sistema completo de autenticación con tokens de acceso y refresco
- 🗃️ **SQLAlchemy** - ORM asíncrono para PostgreSQL
- 🔒 **Seguridad** - Hash de contraseñas con bcrypt, validaciones, CORS
- 🚦 **Rate Limiting** - Protección contra abuso de API
- 📝 **Logging** - Sistema de logs estructurado
- 🎯 **Arquitectura limpia** - Separación de capas (models, schemas, services, endpoints)
- 📚 **Documentación automática** - Swagger UI y ReDoc
- ⚡ **Async/Await** - Operaciones asíncronas para mejor rendimiento

## 📁 Estructura del Proyecto

```
Backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Endpoints de autenticación
│   │       │   └── users.py         # Endpoints de usuarios
│   │       └── router.py            # Router principal v1
│   ├── config/
│   │   ├── database.py              # Configuración de BD
│   │   └── settings.py              # Variables de entorno
│   ├── core/
│   │   ├── exceptions.py            # Excepciones personalizadas
│   │   └── security.py              # JWT y seguridad
│   ├── middleware/
│   │   ├── cors.py                  # Configuración CORS
│   │   ├── error_handler.py         # Manejo de errores
│   │   ├── logging.py               # Middleware de logs
│   │   └── rate_limit.py            # Rate limiting
│   ├── models/
│   │   └── user.py                  # Modelos de BD
│   ├── schemas/
│   │   ├── common.py                # Schemas comunes
│   │   └── user.py                  # Schemas de usuario
│   ├── services/
│   │   └── user_service.py          # Lógica de negocio
│   └── utils/
│       ├── logger.py                # Configuración de logging
│       ├── responses.py             # Utilidades de respuesta
│       └── validators.py            # Validadores personalizados
├── logs/                            # Archivos de log
├── .env                             # Variables de entorno (crear desde .env.example)
├── .env.example                     # Ejemplo de variables de entorno
├── .gitignore                       # Archivos ignorados por git
├── main.py                          # Punto de entrada de la aplicación
└── requirements.txt                 # Dependencias de Python
```

## 🛠️ Instalación

### 1. Clonar o descargar el template

```powershell
cd Backend
```

### 2. Crear entorno virtual

```powershell
python -m venv venv
```

### 3. Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Si tienes problemas de permisos, ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```powershell
Copy-Item .env.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
# Database - Elige una opción:
# PostgreSQL (Recomendado para producción)
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"

# SQLite (Para desarrollo rápido)
# DATABASE_URL="sqlite+aiosqlite:///./database.db"

# JWT - IMPORTANTE: Cambia el SECRET_KEY
SECRET_KEY="tu-clave-secreta-super-segura-cambiala"
```

### 6. Ejecutar la aplicación

```powershell
python main.py
```

O con uvicorn directamente:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Documentación de la API

Una vez que la aplicación esté corriendo, accede a:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔐 Autenticación JWT

### Flujo de autenticación:

1. **Registro**: `POST /api/v1/auth/register`
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123!",
  "full_name": "Nombre Completo"
}
```

2. **Login**: `POST /api/v1/auth/login`
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Respuesta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

3. **Usar el token**: Agrega el header en tus requests:
```
Authorization: Bearer <access_token>
```

4. **Refrescar token**: `POST /api/v1/auth/refresh`
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 🗃️ Base de Datos

### PostgreSQL (Recomendado)

1. Instalar PostgreSQL
2. Crear base de datos:
```sql
CREATE DATABASE nombre_bd;
CREATE USER usuario WITH PASSWORD 'contraseña';
GRANT ALL PRIVILEGES ON DATABASE nombre_bd TO usuario;
```

3. Configurar en `.env`:
```env
DATABASE_URL="postgresql+asyncpg://usuario:contraseña@localhost:5432/nombre_bd"
```

### SQLite (Para desarrollo)

```env
DATABASE_URL="sqlite+aiosqlite:///./database.db"
```

Las tablas se crean automáticamente al iniciar la aplicación.

## 📋 Endpoints Disponibles

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Refrescar token
- `POST /api/v1/auth/logout` - Cerrar sesión

### Usuarios (Requieren autenticación)
- `GET /api/v1/users/me` - Obtener perfil actual
- `PUT /api/v1/users/me` - Actualizar perfil
- `DELETE /api/v1/users/me` - Eliminar cuenta
- `GET /api/v1/users` - Listar usuarios
- `GET /api/v1/users/{id}` - Obtener usuario por ID

## 🧪 Testing

Para crear y ejecutar tests:

```powershell
# Instalar pytest
pip install pytest pytest-asyncio httpx

# Crear carpeta de tests
mkdir tests

# Ejecutar tests
pytest
```

## 🚀 Despliegue en Producción

### Configuraciones importantes:

1. **Cambiar SECRET_KEY**: Genera una clave segura
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Desactivar DEBUG**:
```env
DEBUG=False
ENVIRONMENT=production
```

3. **Configurar CORS** con tus dominios:
```env
CORS_ORIGINS=["https://tudominio.com"]
```

4. **Usar PostgreSQL** en lugar de SQLite

5. **Configurar Redis** para rate limiting y cache

### Desplegar con Docker (Opcional):

Crear `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Personalización

### Agregar un nuevo endpoint:

1. Crear modelo en `app/models/`
2. Crear schemas en `app/schemas/`
3. Crear servicio en `app/services/`
4. Crear endpoint en `app/api/v1/endpoints/`
5. Incluir router en `app/api/v1/router.py`

### Ejemplo de nuevo recurso (productos):

```python
# app/models/product.py
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
```

## 📦 Dependencias Principales

- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `sqlalchemy` - ORM
- `pydantic` - Validación de datos
- `python-jose` - JWT
- `passlib` - Hash de contraseñas
- `slowapi` - Rate limiting
- `redis` - Cache y sesiones
- `celery` - Tareas en background

## 🤝 Contribuir

Este es un template base. Siéntete libre de:
- Agregar nuevas funcionalidades
- Mejorar la estructura
- Optimizar el código
- Agregar tests
- Mejorar la documentación

## 📝 Notas

- Los logs se guardan en `logs/app.log`
- La base de datos se crea automáticamente al iniciar
- El rate limiting protege contra abuso (configurable)
- Todas las contraseñas se hashean con bcrypt
- Los tokens JWT expiran (configurable en `.env`)

## 🐛 Solución de Problemas

### Error de permisos en Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error al conectar a PostgreSQL:
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos exista

### Error de importación de módulos:
```powershell
pip install -r requirements.txt --upgrade
```

## 📄 Licencia

Este template es de uso libre para proyectos personales y comerciales.

---

**¡Listo para desarrollar! 🚀**

Para cualquier duda, revisa la documentación de FastAPI: https://fastapi.tiangolo.com/
