"""
Endpoints de autenticación
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.schemas.user import Token, TokenRefresh, TokenResponse, UserCreate, UserResponse
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.core.security import create_tokens, verify_token
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.middleware.rate_limit import limiter
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.create(db, user_data)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    username = None
    password = None
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        payload = await request.json()
        username = payload.get("username") or payload.get("email")
        password = payload.get("password")
    else:
        form = await request.form()
        username = form.get("username") or form.get("email")
        password = form.get("password")

    if not username or not password:
        raise BadRequestException("Debes enviar usuario/email y contraseña")

    user = await UserService.authenticate(db, username, password)

    if not user:
        raise UnauthorizedException("Email o contraseña incorrectos")

    tokens = create_tokens(user.id, user.email)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        email = payload.get("email")

        user = await UserService.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Usuario no válido")

        tokens = create_tokens(user_id, email)
        return TokenResponse(
            access_token=tokens["access_token"],
            token_type="bearer"
        )

    except Exception:
        raise UnauthorizedException("Token de refresco inválido o expirado")


@router.post("/logout", response_model=MessageResponse)
async def logout():
    return MessageResponse(
        message="Sesión cerrada exitosamente",
        detail="Elimina los tokens del cliente"
    )
