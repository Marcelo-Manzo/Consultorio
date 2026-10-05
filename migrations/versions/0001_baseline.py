"""schema inicial: usuarios, pacientes, consultas, orcamentos, tratamentos

Revision ID: 0001_baseline
Revises:
Create Date: 2026-10-01

Este arquivo substitui o antigo SQL_CREATE_TABLES.txt. A versão anterior estava
desatualizada (faltava a coluna usuario_id, que o app usa em todo filtro).
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "Usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "Pacientes",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=True),
        sa.Column("telefone", sa.String(length=30), nullable=True),
        sa.Column("cpf", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["Usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_pacientes_usuario", "Pacientes", ["usuario_id"])

    op.create_table(
        "Consultas",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("paciente_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.DateTime(), nullable=True),
        sa.Column("tratamento", sa.String(length=150), nullable=True),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("metodo_pagamento", sa.String(length=50), nullable=True),
        sa.Column("compareceu", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("pago", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("duracao", sa.Integer(), server_default=sa.text("30"), nullable=False),
        sa.ForeignKeyConstraint(["paciente_id"], ["Pacientes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["Usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_consultas_usuario", "Consultas", ["usuario_id", "data"])

    op.create_table(
        "Orcamentos",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("consulta_id", sa.Integer(), nullable=True),
        sa.Column("paciente_id", sa.Integer(), nullable=True),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("forma_pagamento", sa.String(length=50), nullable=True),
        sa.Column("status", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("data_criacao", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["consulta_id"], ["Consultas.id"]),
        sa.ForeignKeyConstraint(["paciente_id"], ["Pacientes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["Usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_orcamentos_usuario", "Orcamentos", ["usuario_id"])

    op.create_table(
        "Tratamentos",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=True),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("duracao", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["Usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tratamentos_usuario", "Tratamentos", ["usuario_id"])


def downgrade():
    op.drop_index("idx_tratamentos_usuario", table_name="Tratamentos")
    op.drop_table("Tratamentos")
    op.drop_index("idx_orcamentos_usuario", table_name="Orcamentos")
    op.drop_table("Orcamentos")
    op.drop_index("idx_consultas_usuario", table_name="Consultas")
    op.drop_table("Consultas")
    op.drop_index("idx_pacientes_usuario", table_name="Pacientes")
    op.drop_table("Pacientes")
    op.drop_table("Usuarios")
