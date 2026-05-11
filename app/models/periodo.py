import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Periodo(Base):
    __tablename__ = "periodos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, nullable=False, index=True)
    año = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)  # 1–12
    estado = Column(String, nullable=False, default="activo")  # "activo" | "cerrado"

    # Populated on close only
    resultado_neto = Column(Float, nullable=True)
    total_inversiones_snapshot = Column(Float, nullable=True)
    total_costos_fijos_snapshot = Column(Float, nullable=True)
    ganancia_real = Column(Float, nullable=True)
    ahorro = Column(Float, nullable=True)
    inversion_siguiente = Column(Float, nullable=True)

    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
