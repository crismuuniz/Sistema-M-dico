from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.security import gerar_hash

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE USER
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def criar_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Verificar se o e-mail já existe (Boa prática!)
    user_existente = db.query(models.User).filter(models.User.email == user.email).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    # 2. Gerar hash e preparar objeto
    hashed_password = gerar_hash(user.password)
    
    # IMPORTANTE: Incluir o 'name' que está no seu model e schema
    novo_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    return novo_user


# LISTAR USERS
@router.get("/", response_model=list[schemas.UserResponse])
def listar_users(db: Session = Depends(get_db)):
    # Usamos joinedload para evitar o problema de N+1 consultas ao carregar pacientes/jornadas
    return db.query(models.User).options(joinedload(models.User.pacientes)).all()


# BUSCAR USER POR ID
@router.get("/{user_id}", response_model=schemas.UserResponse)
def buscar_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).options(
        joinedload(models.User.pacientes)
    ).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user


# UPDATE USER
@router.put("/{user_id}", response_model=schemas.UserResponse)
def atualizar_user(user_id: int, dados: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # exclude_unset=True garante que só atualizamos o que foi enviado
    dados_update = dados.model_dump(exclude_unset=True)

    # 1. Trata a senha separadamente
    if "password" in dados_update:
        nova_senha = dados_update.pop("password") # Remove do dict e pega o valor
        if nova_senha: # Só gera se não for string vazia
             db_user.password_hash = gerar_hash(nova_senha)

    # 2. Remove o campo password_hash se ele vier por engano no JSON
    # para evitar que o loop tente gravar um hash manual
    dados_update.pop("password_hash", None)

    # 3. Atualiza os demais campos (name, email, etc)
    for key, value in dados_update.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user


# DELETE USER
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()
    
    # Em DELETE, geralmente retornamos 204 No Content ou apenas uma confirmação
    return Response(status_code=status.HTTP_204_NO_CONTENT)