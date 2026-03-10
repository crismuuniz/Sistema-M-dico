from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime, date, timezone
from typing import List, Optional

# --- EVENTO CLÍNICO ---

class EventoClinicoBase(BaseModel):
    descricao: Optional[str] = None
    # Usando timezone-aware datetime para compatibilidade com Python 3.13
    data_evento: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventoClinicoCreate(EventoClinicoBase):
    jornada_id: int

class EventoClinicoResponse(EventoClinicoBase):
    id: int
    jornada_id: int
    
    # Pydantic v2 usa ConfigDict em vez de class Config
    model_config = ConfigDict(from_attributes=True)

# --- JORNADA ---

class JornadaBase(BaseModel):
    tipo_jornada: str
    data_inicio: date
    status: str
    paciente_id: int
    user_id: int

class JornadaCreate(JornadaBase):
    pass

class JornadaResponse(JornadaBase):
    id: int
    # Para evitar recursão infinita, enviamos apenas os eventos, 
    # sem que o evento tente carregar a jornada de volta.
    eventos_clinicos: List[EventoClinicoResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- PACIENTE ---

class PacienteBase(BaseModel):
    cpf: str
    name: str
    email: Optional[EmailStr] = None # EmailStr valida o formato automaticamente
    telefone: Optional[str] = None
    genero: Optional[str] = None
    data_aniversario: Optional[date] = None

class PacienteCreate(PacienteBase):
    user_id: int
    password: str 

class PacienteUpdate(BaseModel):
    cpf: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    genero: Optional[str] = None
    data_aniversario: Optional[date] = None
    password: Optional[str] = None # Adicionado para permitir trocar senha

class PacienteResponse(PacienteBase):
    id: int
    user_id: int
    # Se o seu model não tiver created_at, remova esta linha para evitar erro 500
    # created_at: datetime 
    jornadas: List[JornadaResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- USUÁRIO (MÉDICO) ---

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    # Aqui listamos os pacientes, mas cuidado: se o PacienteResponse 
    # carregar Jornadas e as Jornadas carregarem Eventos, o JSON ficará gigante.
    pacientes: List[PacienteResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- AUTENTICAÇÃO ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RelatorioCompletoResponse(PacienteResponse):
    """
    Este herda tudo de PacienteResponse, mas podemos usar ele 
    especificamente na rota de relatório para clareza.
    """
    pass