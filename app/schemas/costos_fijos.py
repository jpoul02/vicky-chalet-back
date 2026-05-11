from typing import Optional
from pydantic import BaseModel


class CostoFijoCreate(BaseModel):
    nombre: str
    monto: float
    tipo: str  # "salario" | "alquiler" | "otro"


class CostoFijoUpdate(BaseModel):
    nombre: Optional[str] = None
    monto: Optional[float] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None


class CostoFijoOut(BaseModel):
    id: str
    nombre: str
    monto: float
    tipo: str
    activo: bool

    model_config = {"from_attributes": True}
