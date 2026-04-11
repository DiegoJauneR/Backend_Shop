# Comandos útiles para el desarrollo

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py

# Ejecutar con uvicorn
uvicorn main:app --reload

# Inicializar base de datos
python -m scripts.init_db

# Crear superusuario
python -m scripts.create_superuser

# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Ver logs en tiempo real
Get-Content -Path ".\logs\app.log" -Wait

# Docker - Construir imagen
docker build -t fastapi-backend .

# Docker - Ejecutar contenedor
docker run -d -p 8000:8000 --name fastapi-app fastapi-backend

# Docker Compose - Levantar todos los servicios
docker-compose up -d

# Docker Compose - Ver logs
docker-compose logs -f

# Docker Compose - Detener servicios
docker-compose down

# Docker Compose - Detener y eliminar volúmenes
docker-compose down -v

# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Freeze dependencias actuales
pip freeze > requirements.txt

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Limpiar cache de Python
Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse | Remove-Item -Force -Recurse
