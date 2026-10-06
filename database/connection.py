import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
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
_EH_POSTGRES = DATABASE_URL_ADAPTADA.startswith("postgresql")

# Pool de conexões otimizado para banco remoto (Supabase em sa-east-1, ~15 ms de RTT):
# - AUTOCOMMIT: sem isso toda leitura pagava BEGIN + SELECT + COMMIT (3 ida-e-volta).
#   Nenhuma função do app usa engine.begin()/db.begin(), e nenhuma grava mais de uma
#   linha por transação, então autocommit é seguro e deixa a leitura com 1 ida-e-volta.
# - pre_ping DESLIGADO de propósito: ele custa 1 ida-e-volta em TODA consulta, ou seja
#   dobrava o tempo de abrir qualquer tela. A troca da conexão morta é feita em get_db(),
#   que só paga esse custo quando a conexão realmente caiu.
# - pool_recycle: 60s era desastroso, cada renovação custava ~2,2s de TLS + autenticação.
# - pool_size pequeno: app desktop single-user, não precisa de muitas conexões
connect_args = {}
if _EH_POSTGRES or DATABASE_URL_ADAPTADA.startswith("mssql"):
    # pg8000 usa "timeout"; psycopg2 usaria "connect_timeout"
    connect_args = {"timeout": 15}


def _nada(*args, **kwargs):
    """Substitui commit/rollback que só produziriam warning (ver _anular_commit_spurio)."""
    return None


def _anular_commit_spurio(dbapi_connection, connection_record):
    """Desliga o COMMIT sem transação que o Postgres rejeita com warning.

    Em AUTOCOMMIT cada statement já é confirmada pelo próprio servidor, mas o
    SQLAlchemy continua chamando dbapi.commit() no Session.commit(). O pg8000
    envia "COMMIT" sem olhar se existe transação, e o Postgres responde
    "WARNING: there is no transaction in progress" (fica no log do Supabase).

    Se a engine um dia voltar a usar transação explícita, o commit volta a valer
    normalmente porque o autocommit do pg8000 estará desligado.
    """
    if getattr(dbapi_connection, "autocommit", False):
        dbapi_connection.commit = _nada


opcoes_postgres = {}
if _EH_POSTGRES:
    # não manda ROLLBACK na devolução da conexão ao pool quando há autocommit
    opcoes_postgres["skip_autocommit_rollback"] = True

engine = create_engine(
    DATABASE_URL_ADAPTADA,
    pool_size=3,
    max_overflow=2,
    pool_pre_ping=False,
    pool_recycle=1800,
    isolation_level="AUTOCOMMIT",
    connect_args=connect_args,
    **opcoes_postgres,
)
SessionLocal = sessionmaker(bind=engine)

if _EH_POSTGRES:
    event.listen(engine, "connect", _anular_commit_spurio)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        # antes com o return a func encerrava e nunca fechava a connection, agora com o yeld, ela retorna sem encerrar.
        yield db
    finally:
        db.close()
