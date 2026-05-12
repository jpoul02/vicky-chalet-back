from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.periodo import Periodo
from app.models.usuario import Usuario
from app.schemas.reportes import ResumenAnualItem, TendenciasOut

router = APIRouter()


@router.get("/resumen-anual", response_model=List[ResumenAnualItem])
def resumen_anual(
    año: int = Query(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodos = (
        db.query(Periodo)
        .filter(
            Periodo.usuario_id == current_user.id,
            Periodo.año == año,
            Periodo.estado == "cerrado",
        )
        .order_by(Periodo.mes)
        .all()
    )
    return [
        ResumenAnualItem(
            mes=p.mes,
            año=p.año,
            ganancia_real=p.ganancia_real or 0.0,
            total_egresos=(p.total_inversiones_snapshot or 0.0) + (p.total_costos_fijos_snapshot or 0.0),
            total_inversiones=p.total_inversiones_snapshot or 0.0,
        )
        for p in periodos
    ]


@router.get("/tendencias", response_model=TendenciasOut)
def tendencias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodos = (
        db.query(Periodo)
        .filter(Periodo.usuario_id == current_user.id, Periodo.estado == "cerrado")
        .order_by(Periodo.año, Periodo.mes)
        .limit(12)
        .all()
    )
    meses = [f"{p.año}-{str(p.mes).zfill(2)}" for p in periodos]
    ganancias = [p.ganancia_real or 0.0 for p in periodos]
    egresos = [(p.total_inversiones_snapshot or 0.0) + (p.total_costos_fijos_snapshot or 0.0) for p in periodos]
    inversiones = [p.total_inversiones_snapshot or 0.0 for p in periodos]
    return TendenciasOut(meses=meses, ganancias=ganancias, egresos=egresos, inversiones=inversiones)
