from .connection import get_db
from .contexto import usuario_id_obrigatorio
from .models import Tratamento

# ==================== TRATAMENTOS ====================


def _filtro_usuario():
    return Tratamento.usuario_id == usuario_id_obrigatorio()


def create_tratamento(nome, valor, duracao=None):
    with get_db() as db:
        tratamento = Tratamento(
            nome=nome,
            valor=valor,
            duracao=duracao,
            usuario_id=usuario_id_obrigatorio(),
        )
        db.add(tratamento)
        db.commit()
        db.refresh(tratamento)
        return tratamento.id


def update_tratamento(tratamento_id, nome, valor, duracao):
    with get_db() as db:
        tratamento = (
            db.query(Tratamento)
            .filter(Tratamento.id == tratamento_id, _filtro_usuario())
            .first()
        )
        if tratamento:
            tratamento.nome = nome
            tratamento.valor = valor
            tratamento.duracao = duracao
            db.commit()


def deletar_tratamento(tratamento_id):
    with get_db() as db:
        tratamento = (
            db.query(Tratamento)
            .filter(Tratamento.id == tratamento_id, _filtro_usuario())
            .first()
        )
        if tratamento:
            db.delete(tratamento)
            db.commit()