from unittest.mock import patch, MagicMock
from datetime import datetime
from database.orcamento import (
    criar_orcamento,
    update_orcamento_por_consulta,
    listar_orcamentos_por_mes,
    atualizar_status_orcamento,
    obter_ganho_total_mes,
    lista_orcamentos_por_status_data,
    buscar_orcamento_por_id_consulta,
    deletar_orcamento,
)


@patch("database.orcamento.get_db")
def test_criar_orcamento(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    data = datetime(2026, 8, 31, 10, 0)
    criar_orcamento(1, 1, "150.00", "Pix", data, status=0)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.orcamento.get_db")
def test_update_orcamento_por_consulta(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    update_orcamento_por_consulta(1, 1, "300.00", "Crédito", status=0)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.orcamento.get_db")
def test_listar_orcamentos_por_mes(mock_get_db):
    mock_db = MagicMock()
    mock_orcamento = {"id": 1, "paciente_nome": "João", "valor": 150.00, "status": 0}
    mock_db.execute.return_value.mappings.return_value.fetchall.return_value = [mock_orcamento]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_orcamentos_por_mes(8, 2026)

    assert len(resultado) == 1
    assert resultado[0]["paciente_nome"] == "João"


@patch("database.orcamento.get_db")
def test_listar_orcamentos_por_mes_vazio(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.mappings.return_value.fetchall.return_value = []
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_orcamentos_por_mes(1, 2020)

    assert resultado == []


@patch("database.orcamento.get_db")
def test_atualizar_status_orcamento(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    atualizar_status_orcamento(1, 1)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.orcamento.get_db")
def test_obter_ganho_total_mes(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.scalar.return_value = 500.00
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = obter_ganho_total_mes(8, 2026)

    assert resultado == 500.00


@patch("database.orcamento.get_db")
def test_obter_ganho_total_mes_zero(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.scalar.return_value = 0
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = obter_ganho_total_mes(1, 2020)

    assert resultado == 0


@patch("database.orcamento.get_db")
def test_lista_orcamentos_por_status_data(mock_get_db):
    mock_db = MagicMock()
    mock_orcamento = {"id": 1, "status": 1, "valor": 200.00}
    mock_db.execute.return_value.fetchall.return_value = [mock_orcamento]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    data_inicio = datetime(2026, 8, 1)
    data_fim = datetime(2026, 8, 31)
    resultado = lista_orcamentos_por_status_data(1, data_inicio, data_fim)

    assert len(resultado) == 1
    assert resultado[0]["status"] == 1


@patch("database.orcamento.get_db")
def test_lista_orcamentos_por_status_data_sem_filtro(mock_get_db):
    mock_db = MagicMock()
    mock_orcamento = {"id": 1, "status": 0}
    mock_db.execute.return_value.fetchall.return_value = [mock_orcamento]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = lista_orcamentos_por_status_data(None, None, None)

    assert len(resultado) == 1


@patch("database.orcamento.get_db")
def test_buscar_orcamento_por_id_consulta(mock_get_db):
    mock_db = MagicMock()
    mock_orcamento = [{"id": 1}]
    mock_db.execute.return_value.mappings.return_value.fetchall.return_value = mock_orcamento
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_orcamento_por_id_consulta(1)

    assert len(resultado) == 1
    assert resultado[0]["id"] == 1


@patch("database.orcamento.get_db")
def test_deletar_orcamento(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    deletar_orcamento(1)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
