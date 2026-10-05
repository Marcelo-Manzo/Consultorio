"""row level security ligado nas 5 tabelas

Revision ID: 0002_rls
Revises: 0001_baseline

O Alembic não enxerga RLS, então esta migration existe para deixar o registro
versionado (o banco atual já tem isso ligado). Sem políticas o app continua
funcionando porque o Postgres ignora RLS para o dono das tabelas — e o app
conecta como `postgres`, que é o dono.
"""

from alembic import op

revision = "0002_rls"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None

TABELAS = ("Usuarios", "Pacientes", "Consultas", "Orcamentos", "Tratamentos")


def upgrade():
    for tabela in TABELAS:
        op.execute(f'ALTER TABLE "{tabela}" ENABLE ROW LEVEL SECURITY')


def downgrade():
    for tabela in reversed(TABELAS):
        op.execute(f'ALTER TABLE "{tabela}" DISABLE ROW LEVEL SECURITY')
