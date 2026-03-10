from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas
from app.security import get_current_user 

router = APIRouter(prefix="/jornadas", tags=["Jornadas"])

# CREATE JORNADA (Protegido)
@router.post("/", response_model=schemas.JornadaResponse, status_code=status.HTTP_201_CREATED)
def criar_jornada(
    jornada: schemas.JornadaCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Injeta o usuário logado
):
    # 1. Validação: O paciente deve existir
    paciente = db.query(models.Paciente).filter(models.Paciente.id == jornada.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # 2. Segurança: Forçamos o user_id da jornada a ser o ID do médico logado
    # Isso impede que um médico crie jornadas em nome de outro médico
    dados_jornada = jornada.model_dump()
    dados_jornada["user_id"] = current_user.id 
    
    nova_jornada = models.Jornada(**dados_jornada)

    db.add(nova_jornada)
    db.commit()
    db.refresh(nova_jornada)

    return nova_jornada


# LISTAR JORNADAS (Apenas do usuário logado)
@router.get("/", response_model=list[schemas.JornadaResponse])
def listar_jornadas(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Opcional: Filtramos para que o médico veja apenas as SUAS jornadas
    return db.query(models.Jornada)\
        .options(joinedload(models.Jornada.eventos_clinicos))\
        .filter(models.Jornada.user_id == current_user.id)\
        .all()


# BUSCAR JORNADA POR ID (Verifica se pertence ao usuário)
@router.get("/{jornada_id}", response_model=schemas.JornadaResponse)
def buscar_jornada(
    jornada_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    jornada = db.query(models.Jornada)\
        .options(joinedload(models.Jornada.eventos_clinicos))\
        .filter(models.Jornada.id == jornada_id)\
        .first()

    if not jornada:
        raise HTTPException(status_code=404, detail="Jornada não encontrada")
    
    # Segurança: Impede que um médico veja jornada de paciente de outro médico
    if jornada.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado a esta jornada")

    return jornada