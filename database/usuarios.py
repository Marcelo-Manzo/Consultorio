from .models import Usuario
from.connection import get_db
import bcrypt

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

