from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.usuario import Usuario
from app.schemas.auth import LoginInput, PinLoginInput, UsuarioOut, LoginOut

router = APIRouter()


@router.post("/login", response_model=LoginOut)
def login(body: LoginInput, response: Response, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    token = create_access_token(subject=user.id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="none" if settings.COOKIE_SECURE else "lax",
        secure=settings.COOKIE_SECURE,
        max_age=60 * 60 * 24 * 7,
    )
    return LoginOut(id=user.id, email=user.email, negocio_nombre=user.negocio_nombre, access_token=token)


@router.post("/login-pin", response_model=LoginOut)
def login_pin(body: PinLoginInput, response: Response, db: Session = Depends(get_db)):
    if not settings.AUTH_PIN or body.pin != settings.AUTH_PIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN incorrecto")
    user = db.query(Usuario).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay usuario configurado")
    token = create_access_token(subject=user.id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="none" if settings.COOKIE_SECURE else "lax",
        secure=settings.COOKIE_SECURE,
        max_age=60 * 60 * 24 * 7,
    )
    return LoginOut(id=user.id, email=user.email, negocio_nombre=user.negocio_nombre, access_token=token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"ok": True}


@router.get("/me", response_model=UsuarioOut)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user
