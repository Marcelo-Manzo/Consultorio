
from sqlalchemy import text
from .connection import get_db

# ==================== PACIENTES ====================

def criar_paciente(nome, telefone, cpf):
    #com o with alem de economizar linha, finaliza a func apos o termino
    with get_db() as db:
        query = text("""
            INSERT INTO Pacientes (nome, telefone, cpf)
            VALUES (:nome, :telefone, :cpf)
        """)
        db.execute(query, {"nome": nome, "telefone": telefone, "cpf": cpf})
        db.commit()

def atualizar_paciente(paciente_id, novo_nome, novo_telefone, novo_cpf):
    with get_db() as db:
        query = text("""
            UPDATE Pacientes
            SET nome = :novo_nome,
                telefone = :novo_telefone,
                cpf = :novo_cpf
            WHERE id = :paciente_id
        """)
        db.execute(query, {
            "paciente_id": paciente_id,
            "novo_nome": novo_nome,
            "novo_telefone": novo_telefone, 
            "novo_cpf": novo_cpf
        })
        db.commit()

def listar_pacientes():
    with get_db() as db:
        query = text("SELECT * FROM Pacientes ORDER BY nome")
        result = db.execute(query)
        return result.fetchall()

def buscar_paciente_por_nome(nome):
    with get_db() as db:
        query = text("SELECT * FROM Pacientes WHERE nome LIKE :nome")
        result = db.execute(query, {"nome": f"%{nome}%"})
        return result.fetchall()

def buscar_paciente_por_cpf(cpf):
    with get_db() as db:
        query = text("SELECT * FROM Pacientes WHERE cpf LIKE :cpf")
        result = db.execute(query, {"cpf": f"%{cpf}%"})
        return result.fetchall()

def buscar_paciente_por_id(paciente_id): 
    with get_db() as db:
        query = text("SELECT * FROM Pacientes WHERE id = :id")
        result = db.execute(query, {"id": paciente_id})
        return result.fetchone()

def excluir_paciente_por_id(paciente_id):
    with get_db() as db:
        query = text("DELETE FROM Pacientes WHERE id = :paciente_id")
        db.execute(query, {"paciente_id": paciente_id})
        db.commit()