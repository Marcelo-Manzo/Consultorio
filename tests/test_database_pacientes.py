from unittest.mock import patch, MagicMock
from database.pacientes import (
    criar_paciente,
    atualizar_paciente,
    listar_pacientes,
    buscar_paciente_por_nome,
    buscar_paciente_por_cpf,
    buscar_paciente_por_id,
    excluir_paciente_por_id,
)


@patch("database.pacientes.get_db")
def test_criar_paciente(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    criar_paciente("João Silva", "11999998888", "123.456.789-00")

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.pacientes.get_db")
def test_atualizar_paciente(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    atualizar_paciente(1, "João Santos", "11988887777", "987.654.321-00")

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@patch("database.pacientes.get_db")
def test_listar_pacientes(mock_get_db):
    mock_db = MagicMock()
    mock_paciente = MagicMock()
    mock_paciente.nome = "João"
    mock_db.execute.return_value.fetchall.return_value = [mock_paciente]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_pacientes()

    mock_db.execute.assert_called_once()
    assert len(resultado) == 1
    assert resultado[0].nome == "João"


@patch("database.pacientes.get_db")
def test_listar_pacientes_vazio(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = []
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = listar_pacientes()

    assert resultado == []


@patch("database.pacientes.get_db")
def test_buscar_paciente_por_nome(mock_get_db):
    mock_db = MagicMock()
    mock_paciente = MagicMock()
    mock_paciente.nome = "João Silva"
    mock_db.execute.return_value.fetchall.return_value = [mock_paciente]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_paciente_por_nome("João")

    mock_db.execute.assert_called_once()
    assert len(resultado) == 1
    assert resultado[0].nome == "João Silva"


@patch("database.pacientes.get_db")
def test_buscar_paciente_por_nome_nao_encontrado(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = []
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_paciente_por_nome("Inexistente")

    assert resultado == []


@patch("database.pacientes.get_db")
def test_buscar_paciente_por_cpf(mock_get_db):
    mock_db = MagicMock()
    mock_paciente = MagicMock()
    mock_paciente.cpf = "123.456.789-00"
    mock_db.execute.return_value.fetchall.return_value = [mock_paciente]
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_paciente_por_cpf("123.456.789-00")

    mock_db.execute.assert_called_once()
    assert len(resultado) == 1
    assert resultado[0].cpf == "123.456.789-00"


@patch("database.pacientes.get_db")
def test_buscar_paciente_por_id(mock_get_db):
    mock_db = MagicMock()
    mock_paciente = MagicMock()
    mock_paciente.id = 1
    mock_paciente.nome = "João Silva"
    mock_db.execute.return_value.fetchone.return_value = mock_paciente
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_paciente_por_id(1)

    mock_db.execute.assert_called_once()
    assert resultado.id == 1
    assert resultado.nome == "João Silva"


@patch("database.pacientes.get_db")
def test_buscar_paciente_por_id_nao_encontrado(mock_get_db):
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    resultado = buscar_paciente_por_id(999)

    assert resultado is None


@patch("database.pacientes.get_db")
def test_excluir_paciente_por_id(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_db)

    excluir_paciente_por_id(1)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
