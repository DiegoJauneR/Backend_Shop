"""
Seguridad y autenticación JWT
"""
from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashear contraseña"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token de acceso JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crear token de refresco JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Verificar y decodificar token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verificar tipo de token
        token_type_in_payload = payload.get("type")
        if token_type_in_payload != token_type:
            logger.warning(f"verify_token: tipo incorrecto, esperado='{token_type}' recibido='{token_type_in_payload}'")
            raise credentials_exception
        
        # Verificar expiración
        exp = payload.get("exp")
        now = datetime.utcnow()
        exp_dt = datetime.utcfromtimestamp(exp) if exp else None
        if exp is None or exp_dt < now:
            logger.warning(f"verify_token: token expirado, exp={exp_dt}, now={now}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"verify_token: OK, sub={payload.get('sub')}, type={token_type_in_payload}")
        return payload
        
    except JWTError as e:
        logger.warning(f"verify_token: JWTError: {e}")
        raise credentials_exception


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Dependency para obtener el ID del usuario actual desde el token
    """
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return int(user_id)


def create_tokens(user_id: int, email: str) -> dict:
    """
    Crear par de tokens (acceso y refresco)
    """
    access_token = create_access_token(
        data={"sub": str(user_id), "email": email}
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user_id), "email": email}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
