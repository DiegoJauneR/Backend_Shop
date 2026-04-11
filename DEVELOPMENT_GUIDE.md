# Guía de Desarrollo

## 📋 Buenas Prácticas

### 1. Estructura de Código

- **Mantén la separación de capas**: Modelos → Schemas → Servicios → Endpoints
- **Un archivo por responsabilidad**: No mezcles modelos, schemas y lógica
- **Importaciones absolutas**: Usa `from app.models.user import User` en lugar de importaciones relativas

### 2. Seguridad

#### Contraseñas
```python
# ✅ Correcto
from app.core.security import get_password_hash
hashed = get_password_hash(password)

# ❌ Incorrecto - Nunca guardes contraseñas en texto plano
user.password = password
```

#### JWT Tokens
- Usa tokens de acceso cortos (15-30 minutos)
- Usa refresh tokens más largos (7-30 días)
- Almacena el SECRET_KEY en variables de entorno
- Nunca compartas tokens en logs o errores

#### Variables de Entorno
```python
# ✅ Correcto
from app.config.settings import settings
secret_key = settings.SECRET_KEY

# ❌ Incorrecto
secret_key = "mi-clave-secreta"
```

### 3. Base de Datos

#### Migraciones
- Usa Alembic para migraciones en producción
- Nunca ejecutes `drop_all()` en producción
- Mantén backups regulares

```bash
# Instalar Alembic
pip install alembic

# Inicializar
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "Create users table"

# Aplicar migración
alembic upgrade head
```

#### Queries Eficientes
```python
# ✅ Correcto - Consulta específica
users = await db.execute(
    select(User).where(User.is_active == True).limit(10)
)

# ❌ Incorrecto - Cargar todo en memoria
all_users = await db.execute(select(User))
filtered = [u for u in all_users if u.is_active]
```

### 4. Endpoints

#### Nomenclatura
```python
# ✅ Correcto
@router.get("/users/{user_id}")
@router.post("/users")
@router.put("/users/{user_id}")
@router.delete("/users/{user_id}")

# ❌ Incorrecto
@router.get("/get_user/{id}")
@router.post("/create_user")
```

#### Status Codes
```python
# ✅ Usa los códigos correctos
@router.post("/users", status_code=status.HTTP_201_CREATED)  # Crear
@router.get("/users")  # 200 OK por defecto
@router.put("/users/{id}")  # 200 OK
@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
```

#### Validación
```python
# ✅ Usa Pydantic para validación
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

# ❌ No valides manualmente
if len(username) < 3:
    raise HTTPException(...)
```

### 5. Manejo de Errores

```python
# ✅ Correcto - Usa excepciones personalizadas
from app.core.exceptions import NotFoundException

user = await UserService.get_by_id(db, user_id)
if not user:
    raise NotFoundException("Usuario no encontrado")

# ❌ Incorrecto - HTTPException genérica
if not user:
    raise HTTPException(status_code=404, detail="Not found")
```

### 6. Testing

```python
# ✅ Estructura de test clara
def test_create_user_success():
    """Test de creación exitosa de usuario"""
    # Arrange
    user_data = UserCreate(...)
    
    # Act
    result = await UserService.create(db, user_data)
    
    # Assert
    assert result.email == user_data.email
    assert result.id is not None

# Ejecutar tests
pytest tests/
pytest tests/test_auth.py -v
pytest --cov=app
```

### 7. Logging

```python
# ✅ Correcto
import logging
logger = logging.getLogger(__name__)

logger.info("Usuario creado exitosamente")
logger.error(f"Error al crear usuario: {str(e)}")

# ❌ Incorrecto
print("Usuario creado")  # No usar print
```

### 8. Async/Await

```python
# ✅ Correcto - Operaciones asíncronas
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ❌ Incorrecto - Bloquear el event loop
def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()
```

## 🎯 Arquitectura de Capas

### Models (app/models/)
```python
"""
Define la estructura de la base de datos
Solo SQLAlchemy, sin lógica de negocio
"""
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
```

### Schemas (app/schemas/)
```python
"""
Define estructura de entrada/salida de API
Validación con Pydantic
"""
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
```

### Services (app/services/)
```python
"""
Lógica de negocio
Operaciones de base de datos
"""
class UserService:
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate):
        # Lógica de creación
        pass
```

### Endpoints (app/api/v1/endpoints/)
```python
"""
Rutas de API
Solo coordinación, sin lógica de negocio
"""
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.create(db, user_data)
```

## 🚀 Flujo de Desarrollo

### Agregar un nuevo recurso (ejemplo: Products)

#### 1. Crear modelo
```python
# app/models/product.py
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

#### 2. Crear schemas
```python
# app/schemas/product.py
class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

#### 3. Crear servicio
```python
# app/services/product_service.py
class ProductService:
    @staticmethod
    async def create(db: AsyncSession, product_data: ProductCreate):
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product
```

#### 4. Crear endpoints
```python
# app/api/v1/endpoints/products.py
router = APIRouter(prefix="/products", tags=["Products"])

@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return await ProductService.create(db, product_data)
```

#### 5. Registrar router
```python
# app/api/v1/router.py
from app.api.v1.endpoints import products

api_router.include_router(products.router)
```

## 📦 Dependencias Opcionales

### Alembic (Migraciones)
```bash
pip install alembic
```

### SQLAlchemy Admin
```bash
pip install sqladmin
```

### Sentry (Monitoreo de errores)
```bash
pip install sentry-sdk
```

### APScheduler (Tareas programadas)
```bash
pip install apscheduler
```

## 🐛 Debugging

### VS Code launch.json
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

### Logs detallados
```python
# En .env
DEBUG=True

# En código
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Checklist Pre-Producción

- [ ] Cambiar SECRET_KEY a uno seguro
- [ ] DEBUG=False en producción
- [ ] Configurar CORS con dominios específicos
- [ ] Usar PostgreSQL (no SQLite)
- [ ] Configurar Redis para cache
- [ ] Agregar límites de rate limiting adecuados
- [ ] Configurar logging a archivos
- [ ] Implementar monitoreo (Sentry, etc.)
- [ ] Configurar backups de base de datos
- [ ] Revisar todas las validaciones
- [ ] Agregar tests de integración
- [ ] Documentar endpoints en Swagger
- [ ] Configurar CI/CD
- [ ] Revisar seguridad con herramientas (bandit, safety)

## 🔗 Referencias Útiles

- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- JWT: https://jwt.io/
- PostgreSQL: https://www.postgresql.org/docs/
