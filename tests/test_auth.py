"""
Tests de autenticación
"""
import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)


def test_password_hashing():
    """Test de hash de contraseñas"""
    password = "test_password123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Test de creación de token de acceso"""
    data = {"sub": 1, "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_refresh_token():
    """Test de creación de refresh token"""
    data = {"sub": 1, "email": "test@example.com"}
    token = create_refresh_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token():
    """Test de verificación de token"""
    data = {"sub": 1, "email": "test@example.com"}
    token = create_access_token(data)
    
    payload = verify_token(token, "access")
    
    assert payload is not None
    assert payload.get("sub") == 1
    assert payload.get("email") == "test@example.com"
    assert payload.get("type") == "access"
