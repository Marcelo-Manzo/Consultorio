from datetime import datetime

from database import models
from database.consultas import (
    buscar_consulta_Atual,
    buscar_consulta_por_id,
    buscar_consulta_por_id_dict,
    criar_consulta,
    deletar_consulta,
    listar_consultas_com_paciente_por_data,
    listar_consultas_data,
    listar_consultas_paciente,
    listar_faltas_data,
    listar_tratamentos,
    marcar_comparecimento,
    marcar_pagamento,
    update_consulta,
)

from .conftest import patch_db


def _criar_paciente(db_session, nome="João", cpf="123.456.789-00"):
    p = models.Paciente(nome=nome, telefone="11999998888", cpf=cpf)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _criar_tratamento(db_session, nome="Limpeza", valor=150.0):
    t = models.Tratamento(nome=nome, valor=valor)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


def _criar_consulta(db_session, paciente_id, data=None, tratamento="Limpeza", valor=150.0):
    if data is None:
        data = datetime(2026, 8, 31, 10, 0)
    c = models.Consulta(
        paciente_id=paciente_id,
        tratamento=tratamento,
        data=data,
        valor=valor,
        metodo_pagamento="Pix",
        compareceu=0,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


# ==================== criar_consulta ====================


def test_criar_consulta_retorna_id(db_session):
    p = _criar_paciente(db_session)
    data = datetime(2026, 8, 31, 10, 0)

    with patch_db("consultas", db_session):
        consulta_id = criar_consulta(p.id, "Limpeza", data, 150.0, "Pix")

    assert consulta_id is not None
    with patch_db("consultas", db_session):
        consulta = buscar_consulta_por_id(consulta_id)
    assert consulta is not None
    assert consulta.tratamento == "Limpeza"


# ==================== buscar_consulta_por_id ====================


def test_buscar_consulta_por_id(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(consulta.id)
    assert resultado.id == consulta.id
    assert resultado.tratamento == "Limpeza"


def test_buscar_consulta_por_id_nao_encontrada(db_session):
    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(999)
    assert resultado is None


# ==================== buscar_consulta_por_id_dict ====================


def test_buscar_consulta_por_id_dict(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id_dict(consulta.id)
    assert resultado is not None
    assert resultado["id"] == consulta.id
    assert resultado["tratamento"] == "Limpeza"


def test_buscar_consulta_por_id_dict_nao_encontrada(db_session):
    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id_dict(999)
    assert resultado is None


# ==================== buscar_consulta_Atual ====================


def test_buscar_consulta_atual(db_session):
    p = _criar_paciente(db_session, nome="João")
    data = datetime(2026, 8, 31, 10, 0)
    _criar_consulta(db_session, p.id, data=data)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_Atual(data)
    assert resultado is not None
    assert resultado["nome"] == "João"
    assert resultado["tratamento"] == "Limpeza"


def test_buscar_consulta_atual_nao_encontrada(db_session):
    p = _criar_paciente(db_session)
    data = datetime(2026, 8, 31, 10, 0)
    _criar_consulta(db_session, p.id, data=datetime(2026, 9, 1, 10, 0))

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_Atual(data)
    assert resultado is None


# ==================== deletar_consulta ====================


def test_deletar_consulta(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)

    with patch_db("consultas", db_session):
        deletar_consulta(consulta.id)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(consulta.id)
    assert resultado is None


# ==================== update_consulta ====================


def test_update_consulta(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)
    nova_data = datetime(2026, 9, 15, 14, 30)

    with patch_db("consultas", db_session):
        update_consulta(consulta.id, "Clareamento", nova_data, 300.0, "Crédito")

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(consulta.id)
    assert resultado.tratamento == "Clareamento"
    assert resultado.valor == 300.0
    assert resultado.metodo_pagamento == "Crédito"
    assert resultado.data == nova_data


# ==================== listar_consultas_data ====================


def test_listar_consultas_data(db_session):
    p = _criar_paciente(db_session)
    _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 10, 0))
    _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 14, 0))
    _criar_consulta(db_session, p.id, data=datetime(2026, 9, 1, 10, 0))

    with patch_db("consultas", db_session):
        resultado = listar_consultas_data("2026-08-31")
    assert len(resultado) == 2


def test_listar_consultas_data_vazio(db_session):
    with patch_db("consultas", db_session):
        resultado = listar_consultas_data("2026-08-31")
    assert resultado == []


# ==================== listar_consultas_com_paciente_por_data ====================


def test_listar_consultas_com_paciente_por_data(db_session):
    p = _criar_paciente(db_session, nome="Ana")
    _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 10, 0))

    with patch_db("consultas", db_session):
        resultado = listar_consultas_com_paciente_por_data("2026-08-31")
    assert len(resultado) == 1
    assert resultado[0]["nome"] == "Ana"
    assert resultado[0]["paciente_id"] == p.id


def test_listar_consultas_com_paciente_por_data_ignora_faltas(db_session):
    p = _criar_paciente(db_session)
    c = _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 10, 0))
    c.compareceu = 2  # Faltou
    db_session.commit()

    with patch_db("consultas", db_session):
        resultado = listar_consultas_com_paciente_por_data("2026-08-31")
    assert resultado == []


# ==================== listar_consultas_paciente ====================


def test_listar_consultas_paciente(db_session):
    p = _criar_paciente(db_session)
    _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 10, 0))
    _criar_consulta(db_session, p.id, data=datetime(2026, 9, 1, 10, 0))

    with patch_db("consultas", db_session):
        resultado = listar_consultas_paciente(p.id)
    assert len(resultado) == 2


# ==================== listar_faltas_data ====================


def test_listar_faltas_data(db_session):
    p = _criar_paciente(db_session, nome="Carlos")
    c = _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 10, 0))
    c.compareceu = 2
    db_session.commit()

    with patch_db("consultas", db_session):
        resultado = listar_faltas_data("2026-08-31")
    assert len(resultado) == 1
    assert resultado[0]["nome"] == "Carlos"


def test_listar_faltas_data_nao_mostra_compareceu(db_session):
    p = _criar_paciente(db_session)
    _criar_consulta(db_session, p.id, data=datetime(2026, 8, 31, 10, 0))  # compareceu=0

    with patch_db("consultas", db_session):
        resultado = listar_faltas_data("2026-08-31")
    assert resultado == []


# ==================== marcar_comparecimento ====================


def test_marcar_comparecimento(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)

    with patch_db("consultas", db_session):
        marcar_comparecimento(consulta.id, status=1)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(consulta.id)
    assert resultado.compareceu == 1


def test_marcar_falta(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)

    with patch_db("consultas", db_session):
        marcar_comparecimento(consulta.id, status=2)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(consulta.id)
    assert resultado.compareceu == 2


# ==================== marcar_pagamento ====================


def test_marcar_pagamento(db_session):
    p = _criar_paciente(db_session)
    consulta = _criar_consulta(db_session, p.id)

    with patch_db("consultas", db_session):
        marcar_pagamento(consulta.id, True)

    with patch_db("consultas", db_session):
        resultado = buscar_consulta_por_id(consulta.id)
    assert resultado.pago is True


# ==================== listar_tratamentos ====================


def test_listar_tratamentos(db_session):
    _criar_tratamento(db_session, nome="Limpeza", valor=150.0)
    _criar_tratamento(db_session, nome="Clareamento", valor=500.0)

    with patch_db("consultas", db_session):
        resultado = listar_tratamentos()
    assert len(resultado) == 2
    assert resultado[0].nome in ("Limpeza", "Clareamento")
    assert resultado[0].valor in (150.0, 500.0)


def test_listar_tratamentos_ordem(db_session):
    _criar_tratamento(db_session, nome="Zeta")
    _criar_tratamento(db_session, nome="Alpha")

    with patch_db("consultas", db_session):
        resultado = listar_tratamentos()
    assert [t.nome for t in resultado] == ["Alpha", "Zeta"]


