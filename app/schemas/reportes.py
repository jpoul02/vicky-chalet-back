from typing import List
from pydantic import BaseModel


class ResumenAnualItem(BaseModel):
    mes: int
    año: int
    ganancia_real: float
    total_egresos: float
    total_inversiones: float


class TendenciasOut(BaseModel):
    meses: List[str]
    ganancias: List[float]
    egresos: List[float]
    inversiones: List[float]
