from contextlib import contextmanager
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import models
from database.contexto import definir_usuario
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


@pytest.fixture(autouse=True)
def usuario_logado():
    """Define um usuário no contexto durante todo o teste (multi-usuário).

    O objeto NÃO é persistido no banco: apenas fornece o id ao contexto.
    O id voltado para 999999 para nunca colidir com os usuários reais criados
    nos testes (que usam autoincrement). As funções de banco filtram por
    usuario_atual().id, então todos os dados criados nos testes pertencem a
    esse usuário. Resetado ao fim do teste.
    """
    usuario = models.Usuario(id=999999, nome="Usuário Teste", email="teste@teste.com")
    definir_usuario(usuario)
    yield usuario
    definir_usuario(None)


@pytest.fixture
def insert_paciente(db_session, usuario_logado):
    """Seed de um paciente de teste."""
    def _inserir(nome="João Silva", telefone="11999998888", cpf="123.456.789-00"):
        paciente = models.Paciente(
            nome=nome, telefone=telefone, cpf=cpf, usuario_id=usuario_logado.id
        )
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
