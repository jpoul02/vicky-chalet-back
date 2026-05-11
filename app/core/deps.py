from typing import Generator
from fastapi import Depends, HTTPException, Cookie, Header, status
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.core.security import decode_access_token
from app.core.config import settings
from app.models.usuario import Usuario


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db),
) -> Usuario:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    user_id = decode_access_token(access_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user


def verify_internal_key(x_internal_key: str = Header(default=None)) -> None:
    if not settings.INTERNAL_API_KEY:
        return  # internal auth disabled (dev mode)
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Internal key inválida")
