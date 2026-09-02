from contextlib import contextmanager
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import models
from database.models import Base


@pytest.fixture
def db_session():
    """Cria um banco SQLite em memória com as tabelas do ORM para testes."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def insert_paciente(db_session):
    """Seed de um paciente de teste."""
    def _inserir(nome="João Silva", telefone="11999998888", cpf="123.456.789-00"):
        paciente = models.Paciente(nome=nome, telefone=telefone, cpf=cpf)
        db_session.add(paciente)
        db_session.commit()
        db_session.refresh(paciente)
        return paciente
    return _inserir


@contextmanager
def _use_sqlite_session(db_session):
    """Context manager que entrega a sessão SQLite (imita get_db real)."""
    try:
        yield db_session
    finally:
        pass


def patch_db(module, db_session):
    """Retorna um patch de get_db para um módulo, usando a sessão SQLite."""
    # Cria um NOVO context manager a cada chamada de get_db (context managers
    # não são reutilizáveis).
    return patch(f"database.{module}.get_db", lambda: _use_sqlite_session(db_session))
