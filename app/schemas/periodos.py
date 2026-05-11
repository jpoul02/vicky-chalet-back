from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.inversiones import InversionOut


class CorteResumen(BaseModel):
    periodo_id: str
    total_inversiones: float
    total_costos_fijos: float
    total_egresos: float
    resultado_neto: float
    ganancia_real: float
    margen: float
    ahorro: float
    inversion_siguiente: float


class PeriodoOut(BaseModel):
    id: str
    usuario_id: str
    año: int
    mes: int
    estado: str
    resultado_neto: Optional[float] = None
    total_inversiones_snapshot: Optional[float] = None
    total_costos_fijos_snapshot: Optional[float] = None
    ganancia_real: Optional[float] = None
    ahorro: Optional[float] = None
    inversion_siguiente: Optional[float] = None
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PeriodoDetailOut(PeriodoOut):
    corte: Optional[CorteResumen] = None
    inversiones: List[InversionOut] = []


class PeriodoCreate(BaseModel):
    año: int
    mes: int


class CierrePeriodoInput(BaseModel):
    resultado_neto: float
    ahorro: float
