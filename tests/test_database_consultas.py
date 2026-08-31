from unittest.mock import patch, MagicMock
from datetime import datetime
from database.consultas import (
    criar_consulta,
    buscar_consulta_por_id,
    buscar_consulta_por_id_dict,
    buscar_consulta_Atual,
    deletar_consulta,
    update_consulta,
    listar_consultas_data,
    listar_consultas_com_paciente_por_data,
    listar_consultas_paciente,
    listar_faltas_data,
    marcar_comparecimento,
    marcar_pagamento,
    listar_tratamentos,
)


@patch("database.consultas.get_db")
def test_criar_consulta(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.scalar.return_value = 1
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    data = datetime(2026, 8, 31, 10, 0)
    resultado = criar_consulta(1, "Limpeza", data, "150.00", "Pix")

    assert resultado == 1
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.consultas.get_db")
def test_buscar_consulta_por_id(mock_get_db):
    mock_db = MagicMock()
    mock_consulta = MagicMock()
    mock_consulta.id = 1
    mock_db.execute.return_value.fetchone.return_value = mock_consulta
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_consulta_por_id(1)

    assert resultado.id == 1
    mock_db.execute.assert_called_once()


@patch("database.consultas.get_db")
def test_buscar_consulta_por_id_nao_encontrada(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_consulta_por_id(999)

    assert resultado is None


@patch("database.consultas.get_db")
def test_buscar_consulta_por_id_dict(mock_get_db):
    mock_db = MagicMock()
    mock_consulta = {"id": 1, "tratamento": "Limpeza"}
    mock_db.execute.return_value.mappings.return_value.fetchone.return_value = mock_consulta
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_consulta_por_id_dict(1)

    assert resultado["id"] == 1
    assert resultado["tratamento"] == "Limpeza"


@patch("database.consultas.get_db")
def test_buscar_consulta_atual(mock_get_db):
    mock_db = MagicMock()
    mock_consulta = {"id": 1, "nome": "João", "data": datetime(2026, 8, 31, 10, 0), "tratamento": "Limpeza"}
    mock_db.execute.return_value.mappings.return_value.fetchone.return_value = mock_consulta
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    data = datetime(2026, 8, 31, 10, 0)
    resultado = buscar_consulta_Atual(data)

    assert resultado is not None
    assert resultado["nome"] == "João"


@patch("database.consultas.get_db")
def test_deletar_consulta(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    deletar_consulta(1)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.consultas.get_db")
def test_update_consulta(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    data = datetime(2026, 9, 1, 14, 30)
    update_consulta(1, "Clareamento", data, "300.00", "Crédito")

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.consultas.get_db")
def test_listar_consultas_data(mock_get_db):
    mock_db = MagicMock()
    mock_consulta = MagicMock()
    mock_consulta.data = datetime(2026, 8, 31, 10, 0)
    mock_db.execute.return_value.fetchall.return_value = [mock_consulta]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_consultas_data("2026-08-31")

    assert len(resultado) == 1
    mock_db.execute.assert_called_once()


@patch("database.consultas.get_db")
def test_listar_consultas_paciente(mock_get_db):
    mock_db = MagicMock()
    mock_consulta = MagicMock()
    mock_consulta.paciente_id = 1
    mock_db.execute.return_value.fetchall.return_value = [mock_consulta]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_consultas_paciente(1)

    assert len(resultado) == 1
    assert resultado[0].paciente_id == 1


@patch("database.consultas.get_db")
def test_listar_faltas_data(mock_get_db):
    mock_db = MagicMock()
    mock_falta = {"nome": "João", "tratamento": "Limpeza", "data": datetime(2026, 8, 31, 10, 0)}
    mock_db.execute.return_value.mappings.return_value.fetchall.return_value = [mock_falta]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_faltas_data("2026-08-31")

    assert len(resultado) == 1
    assert resultado[0]["nome"] == "João"


@patch("database.consultas.get_db")
def test_marcar_comparecimento(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    marcar_comparecimento(1, status=1)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.consultas.get_db")
def test_marcar_pagamento(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    marcar_pagamento(1, True)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.consultas.get_db")
def test_listar_tratamentos(mock_get_db):
    mock_db = MagicMock()
    mock_tratamento = MagicMock()
    mock_tratamento.nome = "Limpeza"
    mock_tratamento.valor = 150.00
    mock_db.execute.return_value.fetchall.return_value = [mock_tratamento]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_tratamentos()

    assert len(resultado) == 1
    assert resultado[0].nome == "Limpeza"
    assert resultado[0].valor == 150.00
