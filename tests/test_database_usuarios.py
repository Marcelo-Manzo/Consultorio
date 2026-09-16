from database.models import Usuario
from database.usuarios import (
    create_user,
    delete_user_by_id,
    get_user_by_email,
    get_user_by_id,
    update_user_password,
    validar_senha,
)

from .conftest import patch_db


def test_create_user(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "senha123")

    with patch_db("usuarios", db_session):
        usuarios = db_session.query(Usuario).all()
    assert len(usuarios) == 1
    assert usuarios[0].nome == "Admin"
    assert usuarios[0].email == "admin@consulta.com"


def test_create_user_hashea_senha(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "senha123")

    with patch_db("usuarios", db_session):
        usuario = get_user_by_email("admin@consulta.com")
    assert usuario.senha_hash != "senha123"
    assert validar_senha("senha123", usuario.senha_hash)


def test_senha_nao_armazenada_em_texto_puro(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "segredo")

    with patch_db("usuarios", db_session):
        usuario = get_user_by_email("admin@consulta.com")
    assert "segredo" not in usuario.senha_hash


def test_validar_senha_incorreta(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "senha123")

    with patch_db("usuarios", db_session):
        usuario = get_user_by_email("admin@consulta.com")
    assert not validar_senha("errada", usuario.senha_hash)


def test_get_user_by_id(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "senha123")

    with patch_db("usuarios", db_session):
        usuario_criado = get_user_by_email("admin@consulta.com")

    with patch_db("usuarios", db_session):
        resultado = get_user_by_id(usuario_criado.id)
    assert resultado is not None
    assert resultado.email == "admin@consulta.com"


def test_get_user_by_id_nao_encontrado(db_session):
    with patch_db("usuarios", db_session):
        resultado = get_user_by_id(999)
    assert resultado is None


def test_get_user_by_email_nao_encontrado(db_session):
    with patch_db("usuarios", db_session):
        resultado = get_user_by_email("naoexiste@teste.com")
    assert resultado is None


def test_update_user_password(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "senha123")

    with patch_db("usuarios", db_session):
        usuario_criado = get_user_by_email("admin@consulta.com")

    with patch_db("usuarios", db_session):
        update_user_password(usuario_criado.id, "novaSenha456")

    with patch_db("usuarios", db_session):
        usuario_atualizado = get_user_by_email("admin@consulta.com")
    assert not validar_senha("senha123", usuario_atualizado.senha_hash)
    assert validar_senha("novaSenha456", usuario_atualizado.senha_hash)


def test_update_user_password_inexistente(db_session):
    with patch_db("usuarios", db_session):
        update_user_password(999, "novaSenha456")


def test_delete_user_by_id(db_session):
    with patch_db("usuarios", db_session):
        create_user("Admin", "admin@consulta.com", "senha123")

    with patch_db("usuarios", db_session):
        usuario_criado = get_user_by_email("admin@consulta.com")

    with patch_db("usuarios", db_session):
        delete_user_by_id(usuario_criado.id)

    with patch_db("usuarios", db_session):
        assert get_user_by_email("admin@consulta.com") is None


def test_delete_user_inexistente(db_session):
    with patch_db("usuarios", db_session):
        delete_user_by_id(999)