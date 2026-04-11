# 🚀 Inicio Rápido - 5 minutos

## Instalación Express

### 1. Crear y activar entorno virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```powershell
python main.py
```

¡Listo! La API está corriendo en **http://localhost:8000**

## 📚 Accede a la documentación

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🧪 Prueba rápida con cURL

### 1. Health Check
```powershell
curl http://localhost:8000/health
```

### 2. Registrar usuario
```powershell
$body = @{
    email = "test@example.com"
    username = "testuser"
    password = "TestPass123!"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method Post -Body $body -ContentType "application/json"
```

### 3. Login
```powershell
$body = @{
    email = "test@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
$token = $response.access_token
```

### 4. Obtener perfil (autenticado)
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" -Method Get -Headers $headers
```

## 🎯 Próximos pasos

1. **Cambiar SECRET_KEY**: Genera uno seguro
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Copia el resultado y actualiza en `.env`

2. **Configurar PostgreSQL** (opcional para desarrollo, requerido en producción):
   - Instalar PostgreSQL
   - Crear base de datos
   - Actualizar `DATABASE_URL` en `.env`:
     ```
     DATABASE_URL="postgresql+asyncpg://usuario:password@localhost:5432/nombre_bd"
     ```

3. **Importar colección de Postman**:
   - Abre Postman
   - Import → `postman_collection.json`
   - Ya tienes todos los endpoints listos para probar

4. **Revisar la documentación**:
   - `README.md` - Documentación completa
   - `DEVELOPMENT_GUIDE.md` - Guía de desarrollo
   - `COMMANDS.md` - Comandos útiles

## 🐳 Con Docker (opcional)

```powershell
# Levantar todo (API + PostgreSQL + Redis)
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

## ❓ Problemas comunes

### Error de permisos en PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Módulo no encontrado
```powershell
pip install -r requirements.txt --upgrade
```

### Puerto 8000 en uso
Cambia el puerto en `.env`:
```env
PORT=8001
```

---

**¿Necesitas ayuda?** Revisa `README.md` o `DEVELOPMENT_GUIDE.md` para más detalles.
