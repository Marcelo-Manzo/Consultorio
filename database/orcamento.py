from sqlalchemy import text
from .connection import get_db


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
