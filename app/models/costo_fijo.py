import uuid
from sqlalchemy import Column, String, Float, Boolean
from app.db.base import Base


class CostoFijo(Base):
    __tablename__ = "costos_fijos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    tipo = Column(String, nullable=False)  # "salario" | "alquiler" | "otro"
    activo = Column(Boolean, nullable=False, default=True)
