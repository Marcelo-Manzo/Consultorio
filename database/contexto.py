from .models import Usuario

_usuario_logado = None


def definir_usuario(usuario: Usuario):
    global _usuario_logado
    _usuario_logado = usuario


def usuario_atual() -> Usuario:
    return _usuario_logado