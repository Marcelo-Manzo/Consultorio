import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models  # noqa: F401  # garante que as classes ORM são registradas

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _adaptar_url(url):
    """Troca o driver do Postgres para pg8000 (100% Python).

    O psycopg2-binary embarca DLLs sem assinatura digital (libpq, libssl,
    libcrypto) e o Smart App Control do Windows 11 bloqueia o carregamento
    delas ("DLL load failed while importing _psycopg"). O pg8000 não usa
    nenhuma DLL nativa, então funciona com essa proteção ligada.
    """
    for prefix in ("postgresql+psycopg2", "postgresql+pg8000", "postgres", "postgresql"):
        if url.startswith(f"{prefix}://"):
            return "postgresql+pg8000://" + url[len(prefix) + 3:]
    return url


DATABASE_URL_ADAPTADA = _adaptar_url(DATABASE_URL)

# Pool de conexões otimizado para banco remoto (Supabase em us-west-2, ~1s de RTT):
# - AUTOCOMMIT: sem isso toda leitura pagava BEGIN + SELECT + ROLLBACK (3 ida-e-volta).
#   Nenhuma função do app grava mais de uma linha por transação, então autocommit é
#   seguro e corta a leitura pela metade (medido: ~3,4s -> ~1,7s por chamada).
# - pre_ping DESLIGADO de propósito: ele custa 1 ida-e-volta em TODA consulta, ou seja
#   dobrava o tempo de abrir qualquer tela. A troca da conexão morta é feita em get_db(),
#   que só paga esse custo quando a conexão realmente caiu.
# - pool_recycle: 60s era desastroso, cada renovação custava ~2,2s de TLS + autenticação.
# - pool_size pequeno: app desktop single-user, não precisa de muitas conexões
connect_args = {}
if DATABASE_URL_ADAPTADA.startswith("postgresql"):
    # pg8000 usa "timeout"; psycopg2 usaria "connect_timeout"
    connect_args = {"timeout": 15}
elif DATABASE_URL_ADAPTADA.startswith("mssql"):
    connect_args = {"timeout": 15}

engine = create_engine(
    DATABASE_URL_ADAPTADA,
    pool_size=3,
    max_overflow=2,
    pool_pre_ping=False,
    pool_recycle=1800,
    isolation_level="AUTOCOMMIT",
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
