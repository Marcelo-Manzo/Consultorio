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
        conn.commit()  # CORRIGIDO: Commit na conexão ativa dentro do bloco with

def listar_pacientes():
    db = get_db()
    query = text("SELECT * FROM Pacientes ORDER BY nome")
    with db as conn:
        result = conn.execute(query)
        #fetchall() retorna em dicionarios para o python
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
        conn.commit()  # CORRIGIDO: Commit garantido na conexão ativa dentro do bloco with

def buscar_consulta_por_id(consulta_id):
    """
    Mantida para a Agenda funcionar com objetos puros.
    Acessada via: consulta.data, consulta.tratamento
    """
    db = get_db()
    query = text("""
        SELECT * FROM Consultas 
        WHERE id = :id
    """)
    with db as conn:
        result = conn.execute(query, {"id": consulta_id})
        return result.fetchone()

def buscar_consulta_por_id_dict(consulta_id):
    """
    NOVA FUNÇÃO: Criada especificamente para a tela de Faltantes.
    Retorna um dicionário puro para não quebrar a Agenda.
    Acessada via: consulta['data'], consulta['tratamento']
    """
    db = get_db()
    query = text("""
        SELECT * FROM Consultas 
        WHERE id = :id
    """)
    with db as conn:
        result = conn.execute(query, {"id": consulta_id})
        # .mappings().fetchone() traz uma única linha como dicionário, ou None se o ID não existir
        return result.mappings().fetchone()
    
def buscar_consulta_Atual(data_e_horario):
    db = get_db()
    
    # 1. Ajustamos a query para usar ':data_param' em vez de '?'
    query = text("""
        SELECT c.id, p.nome, c.data, c.tratamento 
        FROM Consultas c
        JOIN Pacientes p ON c.paciente_id = p.id
        WHERE c.data = :data_param AND c.compareceu = 0
    """)
    
    with db as conn:
        # 2. Passamos a chave do dicionário com o MESMO nome que colocamos na query (:data_param)
        # Passamos o objeto datetime direto, pois o SQL Server já sabe comparar com o campo DATETIME
        result = conn.execute(query, {"data_param": data_e_horario})
        return result.mappings().fetchone()

def deletar_consulta(consulta_id):
    db = get_db()
    # Correção: Tiramos a palavra 'values' que causava erro de sintaxe no SQL Server
    query = text("DELETE FROM Consultas WHERE id = :consulta_id")
    with db as conn:
        conn.execute(query, {"consulta_id": consulta_id})
        conn.commit()  # CORRIGIDO: Commit na conexão ativa

def update_consulta(consulta_id, treatment, data_e_horario, valor, metodo_pagamento):
    db = get_db()
    # 2. Escreva o comando de atualização aqui dentro
    query = text("""
        UPDATE Consultas
        SET tratamento = :tratamento,
            data = :data,
            valor = :valor,
            metodo_pagamento = :metodo_pagamento
        WHERE id = :consulta_id
    """)
    with db as conn:
        conn.execute(query, {
            "consulta_id": consulta_id, # Passa o ID da consulta para o WHERE saber qual alterar
            "tratamento": treatment,
            "data": data_e_horario, 
            "valor": valor,
            "metodo_pagamento": metodo_pagamento
        })
        conn.commit()  # CORRIGIDO: Commit na conexão ativa

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

def listar_consultas_com_paciente_por_data(data_selecionada):
    db = get_db()
    query = text("""
        SELECT 
            c.id AS consulta_id,
            c.data,
            c.tratamento,
            c.valor,
            c.metodo_pagamento,
            c.compareceu,
            p.id AS paciente_id,
            p.nome
        FROM Consultas c
        INNER JOIN Pacientes p ON c.paciente_id = p.id
        -- Trocado aqui: CAST converte o DATETIME para o tipo DATE do SQL Server
        WHERE CAST(c.data AS DATE) = :data AND c.compareceu = 0
        ORDER BY c.data ASC
    """)
    with db as conn:
        return conn.execute(query, {"data": data_selecionada}).mappings().all()
    
def listar_consultas_paciente(paciente_id):
    db = get_db()
    query = text("SELECT * FROM Consultas WHERE paciente_id = :id ORDER BY data DESC")
    with db as conn:
        result = conn.execute(query, {"id": paciente_id})
        return result.fetchall()

def listar_faltas_data(data):
    db = get_db()
    query = text("""
        SELECT 
            p.nome, 
            c.tratamento, 
            c.data,
            c.id AS id_consulta,        -- IMPORTANTE: Precisamos do ID da consulta para o botão Concluir/Remarcar
            c.paciente_id AS id_paciente -- IMPORTANTE: Precisamos do ID do paciente para o Duplo Clique
        FROM Consultas c
        JOIN Pacientes p ON c.paciente_id = p.id
        WHERE c.compareceu = 2 AND CONVERT(VARCHAR(10), c.data, 23) = :data
        ORDER BY c.data DESC
    """)
    
    with db as conn:
        # CORREÇÃO 1: Passando o dicionário {"data": data} para preencher o :data do SQL
        result = conn.execute(query, {"data": data})
        
        # CORREÇÃO 2: .mappings().fetchall() garante que o retorno seja lido como dicionário: faltante["nome"]
        return result.mappings().fetchall()

def marcar_comparecimento(consulta_id, status=1):
    db = get_db()
    # Agora aceita :status dinamicamente (pode ser 1 para compareceu, 2 para remarcado, etc.)
    query = text("UPDATE Consultas SET compareceu = :status WHERE id = :id")
    with db as conn:
        conn.execute(query, {"status": status, "id": consulta_id})
        conn.commit()  # Mantido o commit correto na conexão ativa

def marcar_pagamento(consulta_id, pago):
    db = get_db()
    query = text("UPDATE Consultas SET pago = :pago WHERE id = :id")
    with db as conn:
        conn.execute(query, {"pago": pago, "id": consulta_id})
        conn.commit()  # CORRIGIDO: Commit dentro do bloco with

def listar_tratamentos():
    db = get_db()
    query = text("SELECT * FROM Tratamentos ORDER BY nome")
    with db as conn:
        result = conn.execute(query)
        return result.fetchall()