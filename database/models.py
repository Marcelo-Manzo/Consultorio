from sqlalchemy import text
from .connection import get_db

# ==================== PACIENTES ====================

def criar_paciente(nome, telefone, cpf):
    db = get_db()
    query = text("""
        INSERT INTO Pacientes (nome, telefone, cpf)
        VALUES (:nome, :telefone, :cpf)
    """)
    with db as conn:
        conn.execute(query, {"nome": nome, "telefone": telefone, "cpf": cpf})
        db.commit()  # CORRIGIDO: Commit dentro do bloco with

def listar_pacientes():
    db = get_db()
    query = text("SELECT * FROM Pacientes ORDER BY nome")
    with db as conn:
        result = conn.execute(query)
        return result.fetchall()

def buscar_paciente_por_nome(nome):
    db = get_db()
    query = text("SELECT * FROM Pacientes WHERE nome LIKE :nome")
    with db as conn:
        result = conn.execute(query, {"nome": f"%{nome}%"})
        return result.fetchall()

def buscar_paciente_por_id(paciente_id): 
    db = get_db()
    query = text("SELECT * FROM Pacientes WHERE id = :id")
    with db as conn:
        result = conn.execute(query, {"id": paciente_id})
        return result.fetchone()  # Mantido fetchone() para a agenda funcionar

# ==================== CONSULTAS ====================

def criar_consulta(paciente_id, treatment, data_e_horario, valor, metodo_pagamento):
    db = get_db()
    query = text("""
        INSERT INTO Consultas (paciente_id, tratamento, data, valor, metodo_pagamento)
        VALUES (:paciente_id, :tratamento, :data, :valor, :metodo_pagamento)
    """)
    with db as conn:
        conn.execute(query, {
            "paciente_id": paciente_id,
            "tratamento": treatment,
            "data": data_e_horario, 
            "valor": valor,
            "metodo_pagamento": metodo_pagamento
        })
        db.commit()  # CORRIGIDO: Commit garantido dentro do bloco with

def deletar_consulta(consulta_id):
    db = get_db()
    # Correção: Tiramos a palavra 'values' que causava erro de sintaxe no SQL Server
    query = text("DELETE FROM Consultas WHERE id = :consulta_id")
    with db as conn:
        conn.execute(query, {"consulta_id": consulta_id})
        db.commit()

def listar_consultas_data(data):
    db = get_db()
    # DESAFIO CONCLUÍDO: Mudado para ORDER BY data ASC para ordenar os horários na agenda!
    query = text("""
        SELECT * FROM Consultas 
        WHERE CONVERT(VARCHAR(10), data, 23) = :data 
        ORDER BY data ASC
    """)
    with db as conn:
        result = conn.execute(query, {"data": data})
        return result.fetchall()

def listar_consultas_paciente(paciente_id):
    db = get_db()
    query = text("SELECT * FROM Consultas WHERE paciente_id = :id ORDER BY data DESC")
    with db as conn:
        result = conn.execute(query, {"id": paciente_id})
        return result.fetchall()

def listar_faltas():
    db = get_db()
    query = text("""
        SELECT p.nome, c.tratamento, c.data
        FROM Consultas c
        JOIN Pacientes p ON c.paciente_id = p.id
        WHERE c.compareceu = 0
        ORDER BY c.data DESC
    """)
    with db as conn:
        result = conn.execute(query)
        return result.fetchall()

def marcar_comparecimento(consulta_id, compareceu):
    db = get_db()
    query = text("UPDATE Consultas SET compareceu = :compareceu WHERE id = :id")
    with db as conn:
        conn.execute(query, {"compareceu": compareceu, "id": consulta_id})
        db.commit()  # CORRIGIDO: Commit dentro do bloco with

def marcar_pagamento(consulta_id, pago):
    db = get_db()
    query = text("UPDATE Consultas SET pago = :pago WHERE id = :id")
    with db as conn:
        conn.execute(query, {"pago": pago, "id": consulta_id})
        db.commit()  # CORRIGIDO: Commit dentro do bloco with

def listar_tratamentos():
    db = get_db()
    query = text("SELECT * FROM Tratamentos ORDER BY nome")
    with db as conn:
        result = conn.execute(query)
        return result.fetchall()
