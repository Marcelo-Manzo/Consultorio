import re

# ==================== eh_telefone_valido ====================
# Função extraída de views/pacientes.py (definida dentro de mostrar())
# Testada aqui porque não é importável do módulo original.


def eh_telefone_valido(telefone: str) -> bool:
    numeros = re.sub(r"\D", "", telefone)
    if len(numeros) not in (10, 11) or len(set(numeros)) == 1:
        return False
    if len(numeros) == 11:
        ddd = int(numeros[:2])
        if ddd < 11 or ddd > 99 or ddd % 10 == 0 or numeros[2] != "9":
            return False
    return True


def test_telefone_valido_celular():
    assert eh_telefone_valido("(11) 99999-8888") is True


def test_telefone_valido_fixo():
    assert eh_telefone_valido("(11) 3333-4444") is True


def test_telefone_valido_sem_formato():
    assert eh_telefone_valido("11999998888") is True


def test_telefone_valido_celular_ddd_21():
    assert eh_telefone_valido("(21) 99876-5432") is True


def test_telefone_invalido_muito_curto():
    assert eh_telefone_valido("123") is False


def test_telefone_invalido_todos_digitos_iguais():
    assert eh_telefone_valido("(11) 11111-1111") is False


def test_telefone_invalido_ddd_zero():
    assert eh_telefone_valido("(00) 99999-8888") is False


def test_telefone_invalido_ddd_10():
    assert eh_telefone_valido("(10) 99999-8888") is False


def test_telefone_invalido_celular_sem_9():
    assert eh_telefone_valido("(11) 88888-7777") is False


def test_telefone_invalido_vazio():
    assert eh_telefone_valido("") is False


def test_telefone_invalido_so_letras():
    assert eh_telefone_valido("abcde") is False


# ==================== Helper_get_attr ====================


def _helper_get_attr(item, atributo):
    """Cópia de views/orcamento.py para testes (evita import de tkinter)."""
    if isinstance(item, dict):
        return item.get(atributo)
    return getattr(item, atributo, None)


def test_helper_get_attr_dict():
    item = {"nome": "João", "valor": 150}
    assert _helper_get_attr(item, "nome") == "João"
    assert _helper_get_attr(item, "valor") == 150


def test_helper_get_attr_object():
    class Paciente:
        def __init__(self):
            self.nome = "João"
            self.valor = 150

    item = Paciente()
    assert _helper_get_attr(item, "nome") == "João"
    assert _helper_get_attr(item, "valor") == 150


def test_helper_get_attr_chave_inexistente_dict():
    item = {"nome": "João"}
    assert _helper_get_attr(item, "telefone") is None


def test_helper_get_attr_attr_inexistente_objeto():
    class Paciente:
        def __init__(self):
            self.nome = "João"

    item = Paciente()
    assert _helper_get_attr(item, "telefone") is None


def test_helper_get_attr_none():
    assert _helper_get_attr(None, "nome") is None
