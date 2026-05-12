from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.costo_fijo import CostoFijo
from app.models.usuario import Usuario
from app.schemas.costos_fijos import CostoFijoCreate, CostoFijoUpdate, CostoFijoOut

router = APIRouter()


@router.get("", response_model=List[CostoFijoOut])
def list_costos(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(CostoFijo).all()


@router.post("", response_model=CostoFijoOut, status_code=201)
def create_costo(body: CostoFijoCreate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    cf = CostoFijo(**body.model_dump())
    db.add(cf)
    db.commit()
    db.refresh(cf)
    return cf


@router.put("/{cf_id}", response_model=CostoFijoOut)
def update_costo(cf_id: str, body: CostoFijoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    cf = db.query(CostoFijo).filter(CostoFijo.id == cf_id).first()
    if not cf:
        raise HTTPException(status_code=404, detail="Costo fijo no encontrado")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(cf, field, value)
    db.commit()
    db.refresh(cf)
    return cf


@router.delete("/{cf_id}", status_code=204)
def delete_costo(cf_id: str, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    cf = db.query(CostoFijo).filter(CostoFijo.id == cf_id).first()
    if not cf:
        raise HTTPException(status_code=404, detail="Costo fijo no encontrado")
    db.delete(cf)
    db.commit()
