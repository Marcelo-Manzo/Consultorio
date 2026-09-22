import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models  # noqa: F401  # garante que as classes ORM são registradas

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Pool de conexões otimizado para banco remoto (Supabase):
# - pool_recycle: força renovação antes do servidor fechar conexões (evita "connection closed")
# - pool_size pequeno: app desktop single-user, não precisa de muitas conexões
# - pre_ping DESLIGADO: cada query custaria +1 round-trip (~300ms) na nuvem
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args = {"connect_timeout": 15}
elif DATABASE_URL.startswith("mssql"):
    connect_args = {"timeout": 15}

engine = create_engine(
    DATABASE_URL,
    pool_size=3,
    max_overflow=2,
    pool_pre_ping=False,
    pool_recycle=60,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        # antes com o return a func encerrava e nunca fechava a connection, agora com o yeld, ela retorna sem encerrar.
        yield db
    finally:
        db.close()
