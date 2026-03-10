from fastapi import FastAPI
from app.database import engine
from app.models import Base 
from app import models
from app.routers import pacientes, jornadas, eventos, auth, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Sistema Médico",
    version="1.0"
)

app.include_router(pacientes.router)
app.include_router(jornadas.router)
app.include_router(eventos.router)
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/", tags=["Healthcheck"])
def root():
    return {"message": "API Sistema Médico online e operante"}