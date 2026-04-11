"""
Utilidades de validación
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validar fortaleza de contraseña
    Retorna (es_valida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validar username
    Retorna (es_valido, mensaje_error)
    """
    if len(username) < 3:
        return False, "El username debe tener al menos 3 caracteres"
    
    if len(username) > 100:
        return False, "El username no puede exceder 100 caracteres"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "El username solo puede contener letras, números, guiones y guiones bajos"
    
    return True, None
