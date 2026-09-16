import bcrypt

from .connection import get_db
from .models import Usuario


def create_user(nome: str, email: str, senha: str):
    with get_db() as db:
        senha_bytes = senha.encode("utf-8")
        senha_hasheada = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=senha_hasheada,
        )
        db.add(usuario)
        db.commit()

def get_user_by_id(user_id):
    with get_db() as db:
        return db.query(Usuario).filter(Usuario.id == user_id).first()

def get_user_by_email(user_email:str):
    with get_db() as db:
        return db.query(Usuario).filter(Usuario.email == user_email).first()

def update_user_password(user_id:int, nova_senha:str):
    with get_db() as db:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user:
            senha_bytes = nova_senha.encode("utf-8")
            senha_hasheada = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")
            user.senha_hash = senha_hasheada
            db.commit()

def delete_user_by_id(user_id):
    with get_db() as db:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()

def validar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
