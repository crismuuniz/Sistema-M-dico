from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Relacionamentos
    pacientes = relationship("Paciente", back_populates="user", cascade="all, delete")
    # ADICIONADO: Relacionamento com Jornada
    jornadas = relationship("Jornada", back_populates="user", cascade="all, delete")

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    data_aniversario = Column(Date)
    genero = Column(String(20))
    telefone = Column(String(20))
    email = Column(String(100))
    password_hash = Column(String(255))
    # CORREÇÃO: datetime.utcnow sem os parênteses
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="pacientes")
    jornadas = relationship("Jornada", back_populates="paciente", cascade="all, delete")

class Jornada(Base):
    __tablename__ = "jornadas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    tipo_jornada = Column(String(100))
    data_inicio = Column(Date)
    status = Column(String(20))

    paciente = relationship("Paciente", back_populates="jornadas")
    # ADICIONADO/CORRIGIDO: Referência ao User
    user = relationship("User", back_populates="jornadas")
    eventos_clinicos = relationship("EventoClinico", back_populates="jornada", cascade="all, delete")

class EventoClinico(Base):
    __tablename__ = "eventos_clinicos"

    id = Column(Integer, primary_key=True, index=True)
    jornada_id = Column(Integer, ForeignKey("jornadas.id"), nullable=False)
    descricao = Column(String(255))
    # CORREÇÃO: datetime.utcnow sem os parênteses
    data_evento = Column(DateTime, default=datetime.utcnow)

    jornada = relationship("Jornada", back_populates="eventos_clinicos")