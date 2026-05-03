from fastapi import APIRouter

from app.api.v1.endpoints import auth, periodos, inversiones, costos_fijos, reportes, webhook

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(periodos.router, prefix="/periodos", tags=["periodos"])
api_router.include_router(inversiones.router, prefix="/inversiones", tags=["inversiones"])
api_router.include_router(costos_fijos.router, prefix="/costos-fijos", tags=["costos-fijos"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["reportes"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
