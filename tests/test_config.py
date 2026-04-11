"""
Tests de configuración
"""
import pytest
from app.config.settings import settings


def test_settings_loaded():
    """Verificar que la configuración se carga correctamente"""
    assert settings.APP_NAME is not None
    assert settings.API_PREFIX == "/api/v1"


def test_jwt_config():
    """Verificar configuración JWT"""
    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
