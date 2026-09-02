from datetime import datetime

from database import models
from database.orcamento import (
    atualizar_status_orcamento,
    buscar_orcamento_por_id_consulta,
    criar_orcamento,
    deletar_orcamento,
    lista_orcamentos_por_status_data,
    listar_orcamentos_por_mes,
    obter_ganho_total_mes,
    update_orcamento_por_consulta,
)

from .conftest import patch_db


def _criar_paciente(db_session, nome="João", cpf="123.456.789-00"):
    p = models.Paciente(nome=nome, telefone="11999998888", cpf=cpf)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _criar_consulta(db_session, paciente_id, data=None):
    if data is None:
        data = datetime(2026, 8, 31, 10, 0)
    c = models.Consulta(
        paciente_id=paciente_id,
        tratamento="Limpeza",
        data=data,
        valor=150.0,
        metodo_pagamento="Pix",
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


def _criar_orcamento(db_session, consulta_id, paciente_id, valor=150.0, status=0, data_criacao=None):
    if data_criacao is None:
        data_criacao = datetime(2026, 8, 31, 10, 0)
    o = models.Orcamento(
        consulta_id=consulta_id,
        paciente_id=paciente_id,
        valor=valor,
        forma_pagamento="Pix",
        status=status,
        data_criacao=data_criacao,
    )
    db_session.add(o)
    db_session.commit()
    db_session.refresh(o)
    return o


# ==================== criar_orcamento ====================


def test_criar_orcamento(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    data = datetime(2026, 8, 31, 10, 0)

    with patch_db("orcamento", db_session):
        criar_orcamento(c.id, p.id, 150.0, "Pix", data, status=0)

    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(8, 2026)
    assert len(resultado) == 1
    assert resultado[0]["valor"] == 150.0


# ==================== update_orcamento_por_consulta ====================


def test_update_orcamento_por_consulta(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, valor=150.0)

    with patch_db("orcamento", db_session):
        update_orcamento_por_consulta(c.id, p.id, 300.0, "Crédito", status=0)

    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(8, 2026)
    assert resultado[0]["valor"] == 300.0


# ==================== listar_orcamentos_por_mes ====================


def test_listar_orcamentos_por_mes(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, valor=150.0, data_criacao=datetime(2026, 8, 15))

    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(8, 2026)
    assert len(resultado) == 1
    assert resultado[0]["paciente_nome"] == "João"


def test_listar_orcamentos_por_mes_vazio(db_session):
    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(1, 2020)
    assert resultado == []


def test_listar_orcamentos_por_mes_outro_mes_nao_aparece(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, data_criacao=datetime(2026, 9, 5))

    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(8, 2026)
    assert resultado == []


# ==================== atualizar_status_orcamento ====================


def test_atualizar_status_orcamento(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    o = _criar_orcamento(db_session, c.id, p.id, status=0)

    with patch_db("orcamento", db_session):
        atualizar_status_orcamento(o.id, 1)

    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(8, 2026)
    assert resultado[0]["status"] == 1


# ==================== obter_ganho_total_mes ====================


def test_obter_ganho_total_mes(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, valor=100.0, status=1, data_criacao=datetime(2026, 8, 10))
    _criar_orcamento(db_session, c.id, p.id, valor=200.0, status=1, data_criacao=datetime(2026, 8, 20))

    with patch_db("orcamento", db_session):
        total = obter_ganho_total_mes(8, 2026)
    assert total == 300.0


def test_obter_ganho_total_mes_ignora_nao_aprovados(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, valor=100.0, status=0, data_criacao=datetime(2026, 8, 10))
    _criar_orcamento(db_session, c.id, p.id, valor=200.0, status=1, data_criacao=datetime(2026, 8, 20))

    with patch_db("orcamento", db_session):
        total = obter_ganho_total_mes(8, 2026)
    assert total == 200.0


def test_obter_ganho_total_mes_zero(db_session):
    with patch_db("orcamento", db_session):
        total = obter_ganho_total_mes(1, 2020)
    assert total == 0


# ==================== lista_orcamentos_por_status_data ====================


def test_lista_orcamentos_por_status_data_por_status(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, status=0, data_criacao=datetime(2026, 8, 10))
    _criar_orcamento(db_session, c.id, p.id, status=1, data_criacao=datetime(2026, 8, 20))

    with patch_db("orcamento", db_session):
        resultado = lista_orcamentos_por_status_data(1, None, None)
    assert len(resultado) == 1
    assert resultado[0]["status"] == 1


def test_lista_orcamentos_por_status_data_sem_filtro(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, status=0, data_criacao=datetime(2026, 8, 10))
    _criar_orcamento(db_session, c.id, p.id, status=1, data_criacao=datetime(2026, 8, 20))

    with patch_db("orcamento", db_session):
        resultado = lista_orcamentos_por_status_data(None, None, None)
    assert len(resultado) == 2


def test_lista_orcamentos_por_status_data_por_data(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, data_criacao=datetime(2026, 8, 10))
    _criar_orcamento(db_session, c.id, p.id, data_criacao=datetime(2026, 8, 20))

    inicio = datetime(2026, 8, 1)
    fim = datetime(2026, 8, 15)
    with patch_db("orcamento", db_session):
        resultado = lista_orcamentos_por_status_data(None, inicio, fim)
    assert len(resultado) == 1


def test_lista_orcamentos_por_status_data_retorna_paciente(db_session):
    p = _criar_paciente(db_session, nome="Maria")
    c = _criar_consulta(db_session, p.id)
    _criar_orcamento(db_session, c.id, p.id, data_criacao=datetime(2026, 8, 10))

    with patch_db("orcamento", db_session):
        resultado = lista_orcamentos_por_status_data(None, None, None)
    assert resultado[0]["paciente_nome"] == "Maria"
    assert resultado[0]["paciente_cpf"] == p.cpf


# ==================== buscar_orcamento_por_id_consulta ====================


def test_buscar_orcamento_por_id_consulta(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    o = _criar_orcamento(db_session, c.id, p.id)

    with patch_db("orcamento", db_session):
        resultado = buscar_orcamento_por_id_consulta(c.id)
    assert len(resultado) == 1
    assert resultado[0]["id"] == o.id


def test_buscar_orcamento_por_id_consulta_vazio(db_session):
    with patch_db("orcamento", db_session):
        resultado = buscar_orcamento_por_id_consulta(999)
    assert resultado == []


# ==================== deletar_orcamento ====================


def test_deletar_orcamento(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id)
    o = _criar_orcamento(db_session, c.id, p.id)

    with patch_db("orcamento", db_session):
        deletar_orcamento(o.id)

    with patch_db("orcamento", db_session):
        resultado = listar_orcamentos_por_mes(8, 2026)
    assert resultado == []


