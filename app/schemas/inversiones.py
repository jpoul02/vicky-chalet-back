from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class InversionCreate(BaseModel):
    descripcion: str
    monto: float
    tipo: str  # "inicial" | "adicional"
    origen: str = "webapp"
    fecha: Optional[date] = None


class InversionUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[float] = None
    tipo: Optional[str] = None
    fecha: Optional[date] = None


class InversionOut(BaseModel):
    id: str
    periodo_id: str
    descripcion: str
    monto: float
    fecha: date
    tipo: str
    origen: str
    creado_en: datetime

    model_config = {"from_attributes": True}
