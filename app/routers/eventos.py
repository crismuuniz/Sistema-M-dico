from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List

router = APIRouter(prefix="/eventos", tags=["Eventos Clínicos"])

# CREATE EVENTO
@router.post("/", response_model=schemas.EventoClinicoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(evento: schemas.EventoClinicoCreate, db: Session = Depends(get_db)):
    # 1. Validação de Integridade: A jornada pai deve existir
    jornada = db.query(models.Jornada).filter(models.Jornada.id == evento.jornada_id).first()
    if not jornada:
        raise HTTPException(
            status_code=404, 
            detail=f"Jornada com ID {evento.jornada_id} não encontrada. Não é possível criar o evento."
        )

    # 2. Criar o objeto
    novo_evento = models.EventoClinico(**evento.model_dump())

    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)

    return novo_evento


# LISTAR TODOS OS EVENTOS (Geral)
@router.get("/", response_model=List[schemas.EventoClinicoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.EventoClinico).all()


# LISTAR EVENTOS DE UMA JORNADA ESPECÍFICA
@router.get("/jornada/{jornada_id}", response_model=List[schemas.EventoClinicoResponse])
def eventos_da_jornada(jornada_id: int, db: Session = Depends(get_db)):
    # Primeiro verificamos se a jornada existe para dar um feedback melhor
    jornada = db.query(models.Jornada).filter(models.Jornada.id == jornada_id).first()
    if not jornada:
        raise HTTPException(status_code=404, detail="Jornada não encontrada")
    
    return db.query(models.EventoClinico)\
        .filter(models.EventoClinico.jornada_id == jornada_id)\
        .all()


# DELETE EVENTO
@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.EventoClinico).filter(models.EventoClinico.id == evento_id).first()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    db.delete(evento)
    db.commit()
    return None