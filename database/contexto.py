from .models import Usuario

_usuario_logado = None


def definir_usuario(usuario: Usuario):
    global _usuario_logado
    _usuario_logado = usuario


def usuario_atual() -> Usuario:
    return _usuario_logado


def usuario_id_obrigatorio() -> int:
    usuario = usuario_atual()
    if usuario is None:
        raise RuntimeError("Nenhum usuário logado no contexto. Chame definir_usuario() antes.")
    return usuario.id