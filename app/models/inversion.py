import uuid
from sqlalchemy import Column, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Inversion(Base):
    __tablename__ = "inversiones"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    periodo_id = Column(String, nullable=False, index=True)
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(Date, nullable=False)
    tipo = Column(String, nullable=False)    # "inicial" | "adicional"
    origen = Column(String, nullable=False, default="webapp")  # "webapp" | "whatsapp"
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
