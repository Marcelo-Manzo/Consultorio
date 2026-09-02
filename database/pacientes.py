from .connection import get_db
from .models import Paciente

# ==================== PACIENTES ====================


def criar_paciente(nome, telefone, cpf):
    with get_db() as db:
        paciente = Paciente(nome=nome, telefone=telefone, cpf=cpf)
        db.add(paciente)
        db.commit()


def atualizar_paciente(paciente_id, novo_nome, novo_telefone, novo_cpf):
    with get_db() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
        if paciente:
            paciente.nome = novo_nome
            paciente.telefone = novo_telefone
            paciente.cpf = novo_cpf
            db.commit()


def listar_pacientes():
    with get_db() as db:
        return db.query(Paciente).order_by(Paciente.nome).all()


def buscar_paciente_por_nome(nome):
    with get_db() as db:
        return db.query(Paciente).filter(Paciente.nome.like(f"%{nome}%")).all()


def buscar_paciente_por_cpf(cpf):
    with get_db() as db:
        return db.query(Paciente).filter(Paciente.cpf.like(f"%{cpf}%")).all()


def buscar_paciente_por_id(paciente_id):
    with get_db() as db:
        return db.query(Paciente).filter(Paciente.id == paciente_id).first()


def excluir_paciente_por_id(paciente_id):
    with get_db() as db:
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
        if paciente:
            db.delete(paciente)
            db.commit()
