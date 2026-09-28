import keyring

SERVICO = "consultorio"

def salvar_sessao(usuario_id):
    keyring.set_password(SERVICO, "usuario_id", str(usuario_id))

def carregar_sessao():
    try:
        valor = keyring.get_password(SERVICO, "usuario_id")
    except Exception:
        return None          # backend indisponivel -> nao quebra
    return int(valor) if valor else None

def limpar_sessao():
    try:
        keyring.delete_password(SERVICO, "usuario_id")
    except Exception:
        pass