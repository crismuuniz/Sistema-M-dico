from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ALTERE com seus dados
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Crismuniz18!@localhost:3306/sistema"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()