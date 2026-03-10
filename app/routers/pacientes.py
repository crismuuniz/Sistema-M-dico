from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import gerar_hash
from typing import List
from app.security import get_current_user

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


# CREATE
@router.post("/", response_model=schemas.PacienteResponse, status_code=status.HTTP_201_CREATED)
def criar_paciente(
    paciente: schemas.PacienteCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Pega o médico logado
):
    dados = paciente.model_dump()
    
    # Vincula o paciente ao médico logado automaticamente
    dados["user_id"] = current_user.id 

    if "password" in dados and dados["password"]:
        dados["password_hash"] = gerar_hash(dados["password"])
        del dados["password"]

    novo = models.Paciente(**dados)

    novo = models.Paciente(**dados)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


# LISTAR TODOS
@router.get("/", response_model=List[schemas.PacienteResponse])
def listar_pacientes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Retorna apenas os pacientes que pertencem ao médico logado
    return db.query(models.Paciente).filter(models.Paciente.user_id == current_user.id).all()


# BUSCAR POR ID
@router.get("/{paciente_id}", response_model=schemas.PacienteResponse)
def buscar_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()

    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    return paciente


# UPDATE (parcial)
@router.put("/{paciente_id}", response_model=schemas.PacienteResponse)
def atualizar_paciente(paciente_id: int, dados: schemas.PacienteUpdate, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()

    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    # Lógica para atualizar senha se ela vier no update
    update_data = dados.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = gerar_hash(update_data["password"])
        del update_data["password"]

    for key, value in update_data.items():
        setattr(paciente, key, value)

    db.commit()
    db.refresh(paciente)
    return paciente


# DELETE
@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()

    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    db.delete(paciente)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# RELATORIO
@router.get("/{paciente_id}/relatorio", response_model=schemas.PacienteResponse)
def obter_relatorio_paciente(
    paciente_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # O .filter garante a segurança: ID do paciente + ID do médico logado
    paciente = db.query(models.Paciente).filter(
        models.Paciente.id == paciente_id,
        models.Paciente.user_id == current_user.id
    ).first()

    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Paciente não encontrado ou acesso negado."
        )

    return paciente