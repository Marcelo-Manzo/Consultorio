
from sqlalchemy import text
from .connection import get_db

# ==================== PACIENTES ====================

def criar_paciente(nome, telefone, cpf):
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

# ==================== CONSULTAS ====================

def criar_consulta(paciente_id, treatment, data_e_horario, valor, metodo_pagamento, compareceu = 0):
    with get_db() as db:
        query = text("""
            INSERT INTO Consultas (paciente_id, tratamento, data, valor, metodo_pagamento)
            OUTPUT INSERTED.id
            VALUES (:paciente_id, :tratamento, :data, :valor, :metodo_pagamento)
        """)
        result = db.execute(query, {
            "paciente_id": paciente_id,
            "tratamento": treatment,
            "data": data_e_horario,
            "valor": valor,
            "metodo_pagamento": metodo_pagamento,
            "compareceu": compareceu
        })
        consulta_id = result.scalar()
        db.commit()
        return consulta_id

def buscar_consulta_por_id(consulta_id):
    """
    Mantida para a Agenda funcionar com objetos puros.
    Acessada via: consulta.data, consulta.tratamento
    """
    with get_db() as db:
        query = text("""
            SELECT * FROM Consultas 
            WHERE id = :id
        """)
        result = db.execute(query, {"id": consulta_id})
        return result.fetchone()

def buscar_consulta_por_id_dict(consulta_id):
    """
    NOVA FUNÇÃO: Criada especificamente para a tela de Faltantes.
    Retorna um dicionário puro para não quebrar a Agenda.
    Acessada via: consulta['data'], consulta['tratamento']
    """
    with get_db() as db:
        query = text("""
            SELECT * FROM Consultas 
            WHERE id = :id
        """)
        result = db.execute(query, {"id": consulta_id})
        return result.mappings().fetchone()
    
def buscar_consulta_Atual(data_e_horario):
    with get_db() as db:
        query = text("""
            SELECT c.id, p.nome, c.data, c.tratamento 
            FROM Consultas c
            JOIN Pacientes p ON c.paciente_id = p.id
            WHERE c.data = :data_param AND c.compareceu = 0
        """)
        result = db.execute(query, {"data_param": data_e_horario})
        return result.mappings().fetchone()

def deletar_consulta(consulta_id):
    with get_db() as db:
        query = text("DELETE FROM Consultas WHERE id = :consulta_id")
        db.execute(query, {"consulta_id": consulta_id})
        db.commit()

def update_consulta(consulta_id, treatment, data_e_horario, valor, metodo_pagamento):
    with get_db() as db:
        query = text("""
            UPDATE Consultas
            SET tratamento = :tratamento,
                data = :data,
                valor = :valor,
                metodo_pagamento = :metodo_pagamento
            WHERE id = :consulta_id
        """)
        db.execute(query, {
            "consulta_id": consulta_id,
            "tratamento": treatment,
            "data": data_e_horario, 
            "valor": valor,
            "metodo_pagamento": metodo_pagamento
        })
        db.commit()

def listar_consultas_data(data):
    with get_db() as db:
        query = text("""
            SELECT * FROM Consultas 
            WHERE CONVERT(VARCHAR(10), data, 23) = :data 
            ORDER BY data ASC
        """)
        result = db.execute(query, {"data": data})
        return result.fetchall()

def listar_consultas_com_paciente_por_data(data_selecionada):
    with get_db() as db:
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
            WHERE CAST(c.data AS DATE) = :data AND (c.compareceu = 0 OR c.compareceu = 1)
            ORDER BY c.data ASC
        """)
        return db.execute(query, {"data": data_selecionada}).mappings().all()
    
def listar_consultas_paciente(paciente_id):
    with get_db() as db:
        query = text("SELECT * FROM Consultas WHERE paciente_id = :id ORDER BY data DESC")
        result = db.execute(query, {"id": paciente_id})
        return result.fetchall()

def listar_faltas_data(data):
    with get_db() as db:
        query = text("""
            SELECT 
                p.nome, 
                c.tratamento, 
                c.data,
                c.id AS id_consulta,
                c.paciente_id AS id_paciente
            FROM Consultas c
            JOIN Pacientes p ON c.paciente_id = p.id
            WHERE c.compareceu = 2 AND CONVERT(VARCHAR(10), c.data, 23) = :data
            ORDER BY c.data DESC
        """)
        result = db.execute(query, {"data": data})
        return result.mappings().fetchall()

def marcar_comparecimento(consulta_id, status=1):
    with get_db() as db:
        query = text("UPDATE Consultas SET compareceu = :status WHERE id = :id")
        db.execute(query, {"status": status, "id": consulta_id})
        db.commit()

def marcar_pagamento(consulta_id, pago):
    with get_db() as db:
        query = text("UPDATE Consultas SET pago = :pago WHERE id = :id")
        db.execute(query, {"pago": pago, "id": consulta_id})
        db.commit()

def listar_tratamentos():
    with get_db() as db:
        query = text("SELECT * FROM Tratamentos ORDER BY nome")
        result = db.execute(query)
        return result.fetchall()


### orcamentos ####

def criar_orcamento(consulta_id, paciente_id, valor, metodo, data_criacao, status=0):
    with get_db() as db:
        query = text("""
            INSERT INTO Orcamentos (consulta_id, paciente_id, valor, forma_pagamento, status, data_criacao)
            VALUES (:consulta_id, :paciente_id, :valor, :metodo, :status, :data_criacao)
        """)
        db.execute(query, {
            "consulta_id": consulta_id,
            "paciente_id": paciente_id,
            "valor": valor,
            "metodo": metodo,
            "status": status,
            "data_criacao": data_criacao
        })
        db.commit()

def update_orcamento_por_consulta(consulta_id, paciente_id, valor, forma_pagamento, status=0):
    with get_db() as db:
        query = text("""
            UPDATE Orcamentos 
            SET paciente_id = :paciente_id,
                valor = :valor,
                forma_pagamento = :forma_pagamento,
                status = :status
            WHERE consulta_id = :consulta_id
        """)
        db.execute(query, {
            "consulta_id": consulta_id,
            "paciente_id": paciente_id,
            "valor": valor,
            "forma_pagamento": forma_pagamento,
            "status": status
        })
        db.commit()

def listar_orcamentos_por_mes(mes, ano):
    with get_db() as db:
        query = text("""
            SELECT 
                o.id,
                o.consulta_id,
                o.paciente_id,
                p.nome AS paciente_nome,
                o.valor,
                o.forma_pagamento,
                o.status,
                o.data_criacao
            FROM Orcamentos o
            INNER JOIN Pacientes p ON o.paciente_id = p.id
            WHERE MONTH(o.data_criacao) = :mes AND YEAR(o.data_criacao) = :ano
            ORDER BY o.data_criacao DESC
        """)
        result = db.execute(query, {"mes": mes, "ano": ano})
        return result.mappings().fetchall()
    

def atualizar_status_orcamento(orcamento_id, novo_status):
    with get_db() as db:
        query = text("UPDATE Orcamentos SET status = :status WHERE id = :id")
        db.execute(query, {"status": novo_status, "id": orcamento_id})
        db.commit()

def obter_ganho_total_mes(mes, ano):
    with get_db() as db:
        query = text("""
            SELECT COALESCE(SUM(valor), 0) AS total
            FROM Orcamentos
            WHERE status = 1 
              AND MONTH(data_criacao) = :mes 
              AND YEAR(data_criacao) = :ano
        """)
        result = db.execute(query, {"mes": mes, "ano": ano})
        return result.scalar()

def lista_orcamentos_por_status_data(status, data_inicio, data_fim):
    """
    Busca orçamentos filtrando por status e intervalo de datas.

    :param status: Inteiro (0, 1, 2) ou None/String "Todos" para buscar todos os status.
    :param data_inicio: Data inicial no formato 'YYYY-MM-DD' ou objeto date/datetime.
    :param data_fim: Data final no formato 'YYYY-MM-DD' ou objeto date/datetime.
    :return: Lista de registros contendo os dados do orçamento e o nome do paciente.
    """
    with get_db() as db:
        condicoes = ["1=1"]
        params = {}

        if status is not None and str(status).isdigit():
            condicoes.append("o.status = :status")
            params["status"] = int(status)

        if data_inicio:
            condicoes.append("CAST(o.data_criacao AS DATE) >= :data_inicio")
            params["data_inicio"] = data_inicio

        if data_fim:
            condicoes.append("CAST(o.data_criacao AS DATE) <= :data_fim")
            params["data_fim"] = data_fim

        where_clause = " AND ".join(condicoes)

        query = text(f"""
            SELECT 
                o.id,
                o.consulta_id,
                o.paciente_id,
                p.nome AS paciente_nome,
                p.cpf as paciente_cpf,
                o.valor,
                o.forma_pagamento,
                o.status,
                o.data_criacao
            FROM Orcamentos o
            INNER JOIN Pacientes p ON o.paciente_id = p.id 
            WHERE {where_clause}
            ORDER BY o.data_criacao DESC
        """)

        result = db.execute(query, params)
        return result.fetchall()

def buscar_orcamento_por_id_consulta(id_consulta):
    with get_db() as db:
        query = text("""
            SELECT 
                o.id
            FROM Orcamentos o
            INNER JOIN Consultas c ON o.consulta_id = c.id
            WHERE c.id = :id_consulta
        """)
        result = db.execute(query, {"id_consulta": id_consulta})
        return result.mappings().fetchall()

def deletar_orcamento(orcamento_id):
    with get_db() as db:
        query = text("delete from Orcamentos where id = :id")
        db.execute(query, {"id": orcamento_id})
        db.commit()
