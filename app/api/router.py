"""
Router principal de la API
"""
from fastapi import APIRouter
from app.api.endpoints import auth, users, producto, cierre_caja, venta, detalle_venta, boleta

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(producto.router)
api_router.include_router(cierre_caja.router)
api_router.include_router(venta.router)
api_router.include_router(detalle_venta.router)
api_router.include_router(boleta.router)
