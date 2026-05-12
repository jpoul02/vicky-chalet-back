from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, verify_internal_key
from app.models.periodo import Periodo
from app.models.inversion import Inversion
from app.models.costo_fijo import CostoFijo
from app.models.usuario import Usuario
from app.schemas.periodos import PeriodoOut, PeriodoDetailOut, PeriodoCreate, CierrePeriodoInput, CorteResumen

router = APIRouter()


def _compute_corte(db: Session, periodo: Periodo) -> CorteResumen:
    inversiones = db.query(Inversion).filter(Inversion.periodo_id == periodo.id).all()
    costos = db.query(CostoFijo).filter(CostoFijo.activo == True).all()

    total_inv = sum(i.monto for i in inversiones)
    total_cf = sum(c.monto for c in costos)
    total_egresos = total_inv + total_cf
    resultado_neto = periodo.resultado_neto or 0.0
    ganancia_real = resultado_neto - total_egresos
    margen = (ganancia_real / resultado_neto * 100) if resultado_neto else 0.0
    ahorro = periodo.ahorro or 0.0
    inversion_siguiente = ganancia_real - ahorro if ganancia_real > ahorro else 0.0

    return CorteResumen(
        periodo_id=periodo.id,
        total_inversiones=total_inv,
        total_costos_fijos=total_cf,
        total_egresos=total_egresos,
        resultado_neto=resultado_neto,
        ganancia_real=ganancia_real,
        margen=margen,
        ahorro=ahorro,
        inversion_siguiente=inversion_siguiente,
    )


@router.get("", response_model=List[PeriodoOut])
def list_periodos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return (
        db.query(Periodo)
        .filter(Periodo.usuario_id == current_user.id)
        .order_by(Periodo.año.desc(), Periodo.mes.desc())
        .all()
    )


@router.get("/activo", response_model=PeriodoDetailOut)
def get_activo(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodo = (
        db.query(Periodo)
        .filter(Periodo.usuario_id == current_user.id, Periodo.estado == "activo")
        .first()
    )
    if not periodo:
        raise HTTPException(status_code=404, detail="No hay período activo")
    inversiones = db.query(Inversion).filter(Inversion.periodo_id == periodo.id).all()
    return PeriodoDetailOut(
        **PeriodoOut.model_validate(periodo).model_dump(),
        corte=_compute_corte(db, periodo),
        inversiones=inversiones,
    )


@router.get("/activo/bot", response_model=PeriodoDetailOut)
def get_activo_bot(
    db: Session = Depends(get_db),
    _: None = Depends(verify_internal_key),
):
    """Used by WhatsApp bot — authenticates via X-Internal-Key, not user JWT."""
    periodo = db.query(Periodo).filter(Periodo.estado == "activo").first()
    if not periodo:
        raise HTTPException(status_code=404, detail="No hay período activo")
    inversiones = db.query(Inversion).filter(Inversion.periodo_id == periodo.id).all()
    return PeriodoDetailOut(
        **PeriodoOut.model_validate(periodo).model_dump(),
        corte=_compute_corte(db, periodo),
        inversiones=inversiones,
    )


@router.get("/{periodo_id}", response_model=PeriodoDetailOut)
def get_periodo(
    periodo_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodo = db.query(Periodo).filter(
        Periodo.id == periodo_id, Periodo.usuario_id == current_user.id
    ).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    inversiones = db.query(Inversion).filter(Inversion.periodo_id == periodo.id).all()
    return PeriodoDetailOut(
        **PeriodoOut.model_validate(periodo).model_dump(),
        corte=_compute_corte(db, periodo),
        inversiones=inversiones,
    )


@router.post("", response_model=PeriodoOut, status_code=201)
def create_periodo(
    body: PeriodoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    existing_active = db.query(Periodo).filter(
        Periodo.usuario_id == current_user.id, Periodo.estado == "activo"
    ).first()
    if existing_active:
        raise HTTPException(status_code=409, detail="Ya existe un período activo")
    periodo = Periodo(usuario_id=current_user.id, año=body.año, mes=body.mes)
    db.add(periodo)
    db.commit()
    db.refresh(periodo)
    return periodo


@router.patch("/{periodo_id}/cerrar", response_model=CorteResumen)
def cerrar_periodo(
    periodo_id: str,
    body: CierrePeriodoInput,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodo = db.query(Periodo).filter(
        Periodo.id == periodo_id, Periodo.usuario_id == current_user.id
    ).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    if periodo.estado == "cerrado":
        raise HTTPException(status_code=409, detail="El período ya está cerrado")

    corte = _compute_corte(db, periodo)
    ganancia_real = body.resultado_neto - corte.total_egresos
    inversion_siguiente = max(ganancia_real - body.ahorro, 0.0)

    periodo.resultado_neto = body.resultado_neto
    periodo.total_inversiones_snapshot = corte.total_inversiones
    periodo.total_costos_fijos_snapshot = corte.total_costos_fijos
    periodo.ganancia_real = ganancia_real
    periodo.ahorro = body.ahorro
    periodo.inversion_siguiente = inversion_siguiente
    periodo.estado = "cerrado"
    periodo.fecha_cierre = datetime.now(timezone.utc)
    db.commit()
    db.refresh(periodo)

    return CorteResumen(
        periodo_id=periodo.id,
        total_inversiones=corte.total_inversiones,
        total_costos_fijos=corte.total_costos_fijos,
        total_egresos=corte.total_egresos,
        resultado_neto=body.resultado_neto,
        ganancia_real=ganancia_real,
        margen=(ganancia_real / body.resultado_neto * 100) if body.resultado_neto else 0.0,
        ahorro=body.ahorro,
        inversion_siguiente=inversion_siguiente,
    )
