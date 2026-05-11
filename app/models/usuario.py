import uuid
from sqlalchemy import Column, String
from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    negocio_nombre = Column(String, nullable=False, default="Mi Negocio")
