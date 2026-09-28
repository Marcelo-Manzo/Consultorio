from unittest.mock import patch

from database import sessao


def test_salvar_e_carregar():
    with (
        patch.object(sessao.keyring, "set_password") as setter,
        patch.object(sessao.keyring, "get_password", return_value="7"),
    ):
        sessao.salvar_sessao(7)
        assert sessao.carregar_sessao() == 7
        setter.assert_called_once_with("consultorio", "usuario_id", "7")


def test_carregar_sem_sessao():
    with patch.object(sessao.keyring, "get_password", return_value=None):
        assert sessao.carregar_sessao() is None


def test_carregar_erro_backend_retorna_none():
    with patch.object(sessao.keyring, "get_password", side_effect=RuntimeError("no backend")):
        assert sessao.carregar_sessao() is None


def test_limpar_sessao_deleta():
    with patch.object(sessao.keyring, "delete_password") as deleter:
        sessao.limpar_sessao()
        deleter.assert_called_once_with("consultorio", "usuario_id")


def test_limpar_sessao_engole_erro():
    with patch.object(sessao.keyring, "delete_password", side_effect=RuntimeError("no password")):
        sessao.limpar_sessao()