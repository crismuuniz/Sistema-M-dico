from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# O segredo está aqui: importe o módulo dando um "apelido" ou usando o caminho completo
from app import security 
from app.database import get_db
from app import models, schemas
router = APIRouter(tags=["Autenticação"])

@router.post("/login", response_model=schemas.Token) # Adicionado response_model para boa prática
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 1. Busca o usuário
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Validação de usuário e senha (usando o módulo security)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email ou senha incorretos"
        )

    # Corrigido: Referenciando o módulo security para validar a senha
    eh_valido = security.verificar_hash(form_data.password, user.password_hash)
    
    if not eh_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email ou senha incorretos"
        )

    # 3. Geração do Token (também via módulo security)
    token = security.criar_token_acesso(data={"sub": user.email})
    
    return {"access_token": token, "token_type": "bearer"}