from sqlalchemy import func, text

from .connection import get_db
from .models import Consulta, Orcamento, Paciente, Tratamento

# (nome_exibido, model) — útil tanto para a tela de debug quanto para
# qualquer futura funcionalidade que precise listar as tabelas do app.
TABELAS = (
    ("Pacientes", Paciente),
    ("Consultas", Consulta),
    ("Orcamentos", Orcamento),
    ("Tratamentos", Tratamento),
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