from sqlalchemy import text

from .connection import get_db


def criar_consulta(paciente_id, treatment, data_e_horario, valor, metodo_pagamento, compareceu=0):
    with get_db() as db:
        query = text("""
            INSERT INTO Consultas (paciente_id, tratamento, data, valor, metodo_pagamento)
            OUTPUT INSERTED.id
            VALUES (:paciente_id, :tratamento, :data, :valor, :metodo_pagamento)
        """)
        result = db.execute(
            query,
            {
                "paciente_id": paciente_id,
                "tratamento": treatment,
                "data": data_e_horario,
                "valor": valor,
                "metodo_pagamento": metodo_pagamento,
                "compareceu": compareceu,
            },
        )
        consulta_id = result.scalar()
        db.commit()
        return consulta_id


def buscar_consulta_por_id(consulta_id):
    with get_db() as db:
        query = text("SELECT * FROM Consultas WHERE id = :id")
        result = db.execute(query, {"id": consulta_id})
        return result.fetchone()


def buscar_consulta_por_id_dict(consulta_id):
    with get_db() as db:
        query = text("SELECT * FROM Consultas WHERE id = :id")
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
        db.execute(
            query,
            {
                "consulta_id": consulta_id,
                "tratamento": treatment,
                "data": data_e_horario,
                "valor": valor,
                "metodo_pagamento": metodo_pagamento,
            },
        )
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
