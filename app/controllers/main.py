from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import SessionLocal, Usuario, Tarefa
from app.controllers.auth import criar_token, verificar_senha, hash_senha

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ROTAS DE AUTENTICAÇÃO
# =========================

@router.post("/auth/register")
def register(dados: dict, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(
        Usuario.username == dados["username"]
    ).first()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_user = Usuario(
        username=dados["username"],
        password_hash=hash_senha(dados["password"])
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    return {"status": "sucesso"}


@router.post("/auth/login")
def login(dados: dict, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(
        Usuario.username == dados["username"]
    ).first()

    if not user or not verificar_senha(dados["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({"sub": user.username})

    return {"token": token}


# =========================
# ROTAS DE TAREFAS
# =========================

@router.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db)):
    return db.query(Tarefa).all()


@router.post("/tarefas")
def criar_tarefa(dados: dict, db: Session = Depends(get_db)):
    nova_tarefa = Tarefa(
        titulo=dados["titulo"],
        descricao=dados["descricao"],
        data=dados["data"],
        hora=dados["hora"],
        status="pendente"
    )

    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)

    return nova_tarefa


@router.put("/tarefas/{id}")
def editar_tarefa(id: int, dados: dict, db: Session = Depends(get_db)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == id).first()

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    tarefa.titulo = dados.get("titulo", tarefa.titulo)
    tarefa.descricao = dados.get("descricao", tarefa.descricao)
    tarefa.data = dados.get("data", tarefa.data)
    tarefa.hora = dados.get("hora", tarefa.hora)
    tarefa.status = dados.get("status", tarefa.status)

    db.commit()
    db.refresh(tarefa)

    return tarefa


@router.delete("/tarefas/{id}")
def excluir_tarefa(id: int, db: Session = Depends(get_db)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == id).first()

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(tarefa)
    db.commit()

    return {"mensagem": "Tarefa excluída com sucesso"}