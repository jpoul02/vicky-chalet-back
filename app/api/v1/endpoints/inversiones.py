from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, verify_internal_key
from app.models.inversion import Inversion
from app.models.periodo import Periodo
from app.models.usuario import Usuario
from app.schemas.inversiones import InversionCreate, InversionUpdate, InversionOut

router = APIRouter()


@router.get("/periodos/{periodo_id}/inversiones", response_model=List[InversionOut])
def list_inversiones(
    periodo_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodo = db.query(Periodo).filter(
        Periodo.id == periodo_id, Periodo.usuario_id == current_user.id
    ).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    return db.query(Inversion).filter(Inversion.periodo_id == periodo_id).all()


@router.post("/periodos/{periodo_id}/inversiones", response_model=InversionOut, status_code=201)
def create_inversion(
    periodo_id: str,
    body: InversionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    periodo = db.query(Periodo).filter(
        Periodo.id == periodo_id, Periodo.usuario_id == current_user.id
    ).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    if periodo.estado == "cerrado":
        raise HTTPException(status_code=409, detail="No se puede agregar a período cerrado")
    inv = Inversion(
        periodo_id=periodo_id,
        descripcion=body.descripcion,
        monto=body.monto,
        tipo=body.tipo,
        origen=body.origen,
        fecha=body.fecha or date.today(),
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.post("/periodos/activo/bot/inversiones", response_model=InversionOut, status_code=201)
def create_inversion_bot(
    body: InversionCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_internal_key),
):
    """Used by WhatsApp bot — authenticates via X-Internal-Key."""
    periodo = db.query(Periodo).filter(Periodo.estado == "activo").first()
    if not periodo:
        raise HTTPException(status_code=404, detail="No hay período activo")
    if periodo.estado == "cerrado":
        raise HTTPException(status_code=409, detail="Período cerrado")
    inv = Inversion(
        periodo_id=periodo.id,
        descripcion=body.descripcion,
        monto=body.monto,
        tipo=body.tipo,
        origen="whatsapp",
        fecha=body.fecha or date.today(),
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.put("/inversiones/{inversion_id}", response_model=InversionOut)
def update_inversion(
    inversion_id: str,
    body: InversionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    inv = db.query(Inversion).filter(Inversion.id == inversion_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(inv, field, value)
    db.commit()
    db.refresh(inv)
    return inv


@router.delete("/inversiones/{inversion_id}", status_code=204)
def delete_inversion(
    inversion_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    inv = db.query(Inversion).filter(Inversion.id == inversion_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    db.delete(inv)
    db.commit()
