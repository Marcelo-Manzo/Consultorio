from .connection import get_db
from .contexto import usuario_id_obrigatorio
from .models import Paciente

# ==================== PACIENTES ====================


def _filtro_usuario():
    return Paciente.usuario_id == usuario_id_obrigatorio()


def criar_paciente(nome, telefone, cpf):
    with get_db() as db:
        paciente = Paciente(
            nome=nome, telefone=telefone, cpf=cpf, usuario_id=usuario_id_obrigatorio()
        )
        db.add(paciente)
        db.commit()


def atualizar_paciente(paciente_id, novo_nome, novo_telefone, novo_cpf):
    with get_db() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id, _filtro_usuario()).first()
        if paciente:
            paciente.nome = novo_nome
            paciente.telefone = novo_telefone
            paciente.cpf = novo_cpf
            db.commit()


def listar_pacientes():
    with get_db() as db:
        return db.query(Paciente).filter(_filtro_usuario()).order_by(Paciente.nome).all()


def buscar_paciente_por_nome(nome):
    with get_db() as db:
        return db.query(Paciente).filter(_filtro_usuario(), Paciente.nome.like(f"%{nome}%")).all()


def buscar_paciente_por_cpf(cpf):
    with get_db() as db:
        return db.query(Paciente).filter(_filtro_usuario(), Paciente.cpf.like(f"%{cpf}%")).all()


def buscar_paciente_por_id(paciente_id):
    with get_db() as db:
        return db.query(Paciente).filter(Paciente.id == paciente_id, _filtro_usuario()).first()


def excluir_paciente_por_id(paciente_id):
    with get_db() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id, _filtro_usuario()).first()
        if paciente:
            db.delete(paciente)
            db.commit()
