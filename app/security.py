from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import bcrypt
from app.config import settings

# Configurações - Em produção, use variáveis de ambiente!
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Onde o token é gerado (endpoint de login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# --- FUNÇÕES DE HASH (Utilizando bcrypt puro para Python 3.13+) ---

def gerar_hash(password: str) -> str:
    """Transforma senha plana em hash seguro."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verificar_hash(password_plana: str, hashed_password: str) -> bool:
    """Compara senha plana com o hash do banco."""
    try:
        return bcrypt.checkpw(
            password_plana.encode('utf-8'), 
            hashed_password.encode('utf-8') # Corrigido o nome da variável aqui
        )
    except Exception:
        return False
            
# --- FUNÇÕES DE TOKEN JWT ---

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Usando timezone-aware datetime para evitar avisos no Python 3.12+
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- INJEÇÃO DE DEPENDÊNCIA ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Valida o token e retorna o usuário atual do banco."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Busca o usuário no banco de dados
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    return user