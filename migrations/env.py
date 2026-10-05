"""Migrações do Consultório (Alembic).

O schema vem inteiro de database/models.py — não existe mais script .txt
para colar no SQL Editor. As tabelas do Postgres usam aspas porque os nomes
têm maiúsculas ("Consultas", "Pacientes", ...).

Fluxo normal:

    alembic upgrade head                 # aplica o que falta no banco do .env
    alembic revision --autogenerate -m "descricao"   # gera a migration
    alembic downgrade -1                 # desfaz a última

Para conferir se o banco bate com os models (sem escrever nada):

    alembic check
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# o .env aponta para o banco; o app já sabe falar com ele (driver, timeout, etc)
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from database.connection import DATABASE_URL_ADAPTADA  # noqa: E402
from database.models import Base  # noqa: E402

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL_ADAPTADA.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Gera o SQL das migrations sem tocar no banco (--sql)."""
    context.configure(
        url=DATABASE_URL_ADAPTADA,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
