from database.consultas import listar_tratamentos
from database.contexto import definir_usuario
from database.models import Tratamento, Usuario
from database.tratamentos import (
    create_tratamento,
    deletar_tratamento,
    update_tratamento,
)

from .conftest import patch_db


def _criar(db_session, nome, valor, duracao=None):
    t = Tratamento(nome=nome, valor=valor, duracao=duracao, usuario_id=999999)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


# ==================== Criar ====================


def test_create_tratamento(db_session):
    with patch_db("tratamentos", db_session):
        create_tratamento("Limpeza", 150.0)

    with patch_db("tratamentos", db_session):
        tratamentos = db_session.query(Tratamento).all()
    assert len(tratamentos) == 1
    assert tratamentos[0].nome == "Limpeza"
    assert tratamentos[0].valor == 150.0


def test_create_tratamento_sem_duracao_fica_null(db_session):
    with patch_db("tratamentos", db_session):
        create_tratamento("Limpeza", 150.0)

    with patch_db("tratamentos", db_session):
        tratamentos = db_session.query(Tratamento).all()
    assert tratamentos[0].duracao is None


def test_create_tratamento_com_duracao(db_session):
    with patch_db("tratamentos", db_session):
        create_tratamento("Clareamento", 500.0, duracao=60)

    with patch_db("tratamentos", db_session):
        tratamentos = db_session.query(Tratamento).all()
    assert tratamentos[0].duracao == 60


def test_create_tratamento_retorna_id(db_session):
    with patch_db("tratamentos", db_session):
        id_criado = create_tratamento("Limpeza", 150.0)
    with patch_db("tratamentos", db_session):
        tratamento = db_session.query(Tratamento).filter(Tratamento.id == id_criado).first()
    assert tratamento is not None


# ==================== Atualizar ====================


def test_update_tratamento(db_session):
    t = _criar(db_session, "Limpeza", 150.0, duracao=30)

    with patch_db("tratamentos", db_session):
        update_tratamento(t.id, "Limpeza Profunda", 200.0, duracao=45)

    with patch_db("tratamentos", db_session):
        atualizado = db_session.query(Tratamento).get(t.id)
    assert atualizado.nome == "Limpeza Profunda"
    assert atualizado.valor == 200.0
    assert atualizado.duracao == 45


def test_update_tratamento_pode_limpar_duracao(db_session):
    t = _criar(db_session, "Limpeza", 150.0, duracao=30)

    with patch_db("tratamentos", db_session):
        update_tratamento(t.id, "Limpeza", 150.0, duracao=None)

    with patch_db("tratamentos", db_session):
        atualizado = db_session.query(Tratamento).get(t.id)
    assert atualizado.duracao is None


def test_update_tratamento_inexistente_nao_levanta(db_session):
    with patch_db("tratamentos", db_session):
        update_tratamento(999, "X", 1.0, duracao=None)


# ==================== Excluir ====================


def test_deletar_tratamento(db_session):
    t = _criar(db_session, "Limpeza", 150.0)

    with patch_db("tratamentos", db_session):
        deletar_tratamento(t.id)

    with patch_db("tratamentos", db_session):
        restantes = db_session.query(Tratamento).all()
    assert restantes == []


def test_deletar_tratamento_inexistente_nao_levanta(db_session):
    with patch_db("tratamentos", db_session):
        deletar_tratamento(999)


# ==================== Isolamento Multi-Usuário ====================


def _criar_usuario(db_session, nome="Outro"):
    usuario = Usuario(nome=nome, email=f"{nome.lower()}@teste.com")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def test_listar_tratamentos_so_do_usuario_logado(db_session, usuario_logado):
    _criar(db_session, "Limpeza", 150.0)
    outro = _criar_usuario(db_session)

    definir_usuario(outro)
    try:
        with patch_db("consultas", db_session):
            tratamentos = listar_tratamentos()
        assert tratamentos == []
    finally:
        definir_usuario(usuario_logado)

    with patch_db("consultas", db_session):
        tratamentos = listar_tratamentos()
    assert len(tratamentos) == 1


def test_atualizar_tratamento_de_outro_usuario_nao_altera(db_session, usuario_logado):
    t = _criar(db_session, "Limpeza", 150.0, duracao=30)
    outro = _criar_usuario(db_session)

    definir_usuario(outro)
    try:
        with patch_db("tratamentos", db_session):
            update_tratamento(t.id, "Hacked", 1.0, duracao=None)
    finally:
        definir_usuario(usuario_logado)

    with patch_db("tratamentos", db_session):
        resultado = db_session.query(Tratamento).get(t.id)
    assert resultado.nome == "Limpeza"
    assert resultado.valor == 150.0
    assert resultado.duracao == 30


def test_deletar_tratamento_de_outro_usuario_nao_exclui(db_session, usuario_logado):
    t = _criar(db_session, "Limpeza", 150.0)
    outro = _criar_usuario(db_session)

    definir_usuario(outro)
    try:
        with patch_db("tratamentos", db_session):
            deletar_tratamento(t.id)
    finally:
        definir_usuario(usuario_logado)

    with patch_db("tratamentos", db_session):
        resultado = db_session.query(Tratamento).get(t.id)
    assert resultado is not None