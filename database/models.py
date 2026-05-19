from sqlalchemy import text
from .connection import get_db
#onde ficam as funções com o banco
# ==================== PACIENTES ====================

def criar_paciente(nome, telefone, cpf):
    db = get_db()
    query = text("""
        INSERT INTO Pacientes (nome, telefone, cpf)
        VALUES (:nome, :telefone, :cpf)
    """)
    db.execute(query, {"nome": nome, "telefone": telefone, "cpf": cpf})
    db.commit()

def listar_pacientes():
    db = get_db()
    query = text("SELECT * FROM Pacientes ORDER BY nome")
    result = db.execute(query)
    return result.fetchall()

def buscar_paciente_por_nome(nome):
    db = get_db()
    query = text("SELECT * FROM Pacientes WHERE nome LIKE :nome")
    result = db.execute(query, {"nome": f"%{nome}%"})
    return result.fetchall()

def buscar_paciente_por_id(paciente_id): 
    db = get_db()
    query = text("SELECT * FROM Pacientes WHERE id = :id")
    result = db.execute(query, {"id": paciente_id})
    return result.fetchall()

# ==================== CONSULTAS ====================

def criar_consulta(paciente_id, tratamento, data,horaio, valor, metodo_pagamento):
    db = get_db()
    query = text("""
        INSERT INTO Consultas (paciente_id, tratamento, data, horario, valor, metodo_pagamento)
        VALUES (:paciente_id, :tratamento, :data, :horario, :valor, :metodo_pagamento)
    """)
    db.execute(query, {
        "paciente_id": paciente_id,
        "tratamento": tratamento,
        "data": data,
        "horario": horaio,
        "valor": valor,
        "metodo_pagamento": metodo_pagamento
    })
    db.commit()

def listar_consultas_data(data):
    db = get_db()
    # Convertemos o campo 'data' do SQL Server para o formato YYYY-MM-DD (código 23) antes de comparar
    query = text("""
        SELECT * FROM Consultas 
        WHERE CONVERT(VARCHAR(10), data, 23) = :data 
        ORDER BY data DESC
    """)
    result = db.execute(query, {"data": data})
    return result.fetchall()

def listar_consultas_paciente(paciente_id):
    db = get_db()
    query = text("SELECT * FROM Consultas WHERE paciente_id = :id ORDER BY data DESC")
    result = db.execute(query, {"id": paciente_id})
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
    result = db.execute(query)
    return result.fetchall()

def marcar_comparecimento(consulta_id, compareceu):
    db = get_db()
    query = text("UPDATE Consultas SET compareceu = :compareceu WHERE id = :id")
    db.execute(query, {"compareceu": compareceu, "id": consulta_id})
    db.commit()

def marcar_pagamento(consulta_id, pago):
    db = get_db()
    query = text("UPDATE Consultas SET pago = :pago WHERE id = :id")
    db.execute(query, {"pago": pago, "id": consulta_id})
    db.commit()

def listar_tratamentos():
    db = get_db()
    query = text("SELECT * FROM Tratamentos ORDER BY nome")
    result = db.execute(query)
    return result.fetchall()

# ==================== Agenda ====================