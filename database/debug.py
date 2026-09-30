from sqlalchemy import func, text

from .connection import get_db
from .models import Consulta, Orcamento, Paciente, Tratamento, Usuario

# (nome_exibido, model) — útil tanto para a tela de debug quanto para
# qualquer futura funcionalidade que precise listar as tabelas do app.
TABELAS = (
    ("Pacientes", Paciente),
    ("Consultas", Consulta),
    ("Orcamentos", Orcamento),
    ("Tratamentos", Tratamento),
    ("Usuarios", Usuario),
)


def testar_conexao():
    """Valida a conexão com o banco de dados (sobe exceção se falhar)."""
    with get_db() as db:
        db.execute(text("SELECT 1"))


def contar_registros():
    """Conta o total de registros por tabela (diagnóstico global).

    Retorna um dict {nome_tabela: quantidade}.
    """
    with get_db() as db:
        return {nome: db.query(func.count(modelo.id)).scalar() for nome, modelo in TABELAS}


def corrigir_sequencias():
    """Ajusta as sequências (SERIAL/IDENTITY) do Postgres para o maior id de cada tabela.

    Necessário após importar dados de outro banco (ex: SQL Server): sem isso o
    nextval devolve um id já existente e o INSERT quebra com UniqueViolation
    ("duplicate key"), o que aparece como erro ao salvar no app.
    """
    with get_db() as db:
        for nome, modelo in TABELAS:
            tabela = '"' + modelo.__tablename__ + '"'
            sql = text(
                "SELECT setval(pg_get_serial_sequence('" + tabela + "', 'id'), "
                "COALESCE((SELECT MAX(id) FROM " + tabela + "), 1), true)"
            )
            db.execute(sql)