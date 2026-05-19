from fastapi import FastAPI
from app.controllers.main import router
from app.models.database import init_db

app = FastAPI(title="API Agenda de Tarefas")

init_db()

app.include_router(router)


@app.get("/")
def home():
    return {"mensagem": "API Agenda de Tarefas rodando"}