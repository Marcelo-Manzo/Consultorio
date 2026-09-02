from database.pacientes import (
    atualizar_paciente,
    buscar_paciente_por_cpf,
    buscar_paciente_por_id,
    buscar_paciente_por_nome,
    criar_paciente,
    excluir_paciente_por_id,
    listar_pacientes,
)

from .conftest import patch_db

# ==================== Testes ====================
# (substituições manuais: _patch_db -> patch_db)


def test_criar_paciente(db_session):
    with patch_db("pacientes", db_session):
        criar_paciente("João Silva", "11999998888", "123.456.789-00")

    with patch_db("pacientes", db_session):
        pacientes = listar_pacientes()
    assert len(pacientes) == 1
    assert pacientes[0].nome == "João Silva"
    assert pacientes[0].cpf == "123.456.789-00"


def test_criar_paciente_multiplo(db_session):
    with patch_db("pacientes", db_session):
        criar_paciente("Ana", "11988887777", "987.654.321-00")
        criar_paciente("Bruno", "11888887777", "111.222.333-44")

    with patch_db("pacientes", db_session):
        pacientes = listar_pacientes()
    assert len(pacientes) == 2


def test_atualizar_paciente(db_session, insert_paciente):
    paciente = insert_paciente()

    with patch_db("pacientes", db_session):
        atualizar_paciente(paciente.id, "João Santos", "11988887777", "987.654.321-00")

    with patch_db("pacientes", db_session):
        atualizado = buscar_paciente_por_id(paciente.id)
    assert atualizado.nome == "João Santos"
    assert atualizado.telefone == "11988887777"
    assert atualizado.cpf == "987.654.321-00"


def test_listar_pacientes_ordem_alfabetica(db_session, insert_paciente):
    insert_paciente(nome="Zeca")
    insert_paciente(nome="Ana")

    with patch_db("pacientes", db_session):
        pacientes = listar_pacientes()
    assert [p.nome for p in pacientes] == ["Ana", "Zeca"]


def test_listar_pacientes_vazio(db_session):
    with patch_db("pacientes", db_session):
        pacientes = listar_pacientes()
    assert pacientes == []


def test_buscar_paciente_por_nome(db_session, insert_paciente):
    insert_paciente(nome="João Silva")

    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_nome("João")
    assert len(resultado) == 1
    assert resultado[0].nome == "João Silva"


def test_buscar_paciente_por_nome_parcial(db_session, insert_paciente):
    insert_paciente(nome="Maria Joaquina")
    insert_paciente(nome="Maria Antonia")

    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_nome("Maria")
    assert len(resultado) == 2


def test_buscar_paciente_por_nome_nao_encontrado(db_session):
    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_nome("Inexistente")
    assert resultado == []


def test_buscar_paciente_por_cpf(db_session, insert_paciente):
    insert_paciente(cpf="123.456.789-00")

    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_cpf("123.456.789-00")
    assert len(resultado) == 1
    assert resultado[0].cpf == "123.456.789-00"


def test_buscar_paciente_por_cpf_parcial(db_session, insert_paciente):
    insert_paciente(cpf="123.456.789-00")

    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_cpf("123")
    assert len(resultado) == 1


def test_buscar_paciente_por_id(db_session, insert_paciente):
    paciente = insert_paciente()

    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_id(paciente.id)
    assert resultado is not None
    assert resultado.id == paciente.id
    assert resultado.nome == "João Silva"


def test_buscar_paciente_por_id_nao_encontrado(db_session):
    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_id(999)
    assert resultado is None


def test_excluir_paciente_por_id(db_session, insert_paciente):
    paciente = insert_paciente()

    with patch_db("pacientes", db_session):
        excluir_paciente_por_id(paciente.id)

    with patch_db("pacientes", db_session):
        resultado = buscar_paciente_por_id(paciente.id)
    assert resultado is None


