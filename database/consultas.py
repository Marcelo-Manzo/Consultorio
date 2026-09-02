from datetime import datetime, timedelta

from .connection import get_db
from .models import Consulta, Paciente, Tratamento


def criar_consulta(paciente_id, treatment, data_e_horario, valor, metodo_pagamento, compareceu=0):
    with get_db() as db:
        consulta = Consulta(
            paciente_id=paciente_id,
            tratamento=treatment,
            data=data_e_horario,
            valor=valor,
            metodo_pagamento=metodo_pagamento,
            compareceu=compareceu,
        )
        db.add(consulta)
        db.commit()
        db.refresh(consulta)
        return consulta.id


def buscar_consulta_por_id(consulta_id):
    with get_db() as db:
        return db.query(Consulta).filter(Consulta.id == consulta_id).first()


def buscar_consulta_por_id_dict(consulta_id):
    with get_db() as db:
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        if not consulta:
            return None
        return {
            "id": consulta.id,
            "paciente_id": consulta.paciente_id,
            "data": consulta.data,
            "tratamento": consulta.tratamento,
            "valor": consulta.valor,
            "metodo_pagamento": consulta.metodo_pagamento,
            "compareceu": consulta.compareceu,
        }


def buscar_consulta_Atual(data_e_horario):
    with get_db() as db:
        consulta = (
            db.query(Consulta, Paciente)
            .join(Paciente, Consulta.paciente_id == Paciente.id)
            .filter(Consulta.data == data_e_horario, Consulta.compareceu == 0)
            .first()
        )
        if not consulta:
            return None
        c, p = consulta
        return {
            "id": c.id,
            "nome": p.nome,
            "data": c.data,
            "tratamento": c.tratamento,
        }


def deletar_consulta(consulta_id):
    with get_db() as db:
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        if consulta:
            db.delete(consulta)
            db.commit()


def update_consulta(consulta_id, treatment, data_e_horario, valor, metodo_pagamento):
    with get_db() as db:
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        if consulta:
            consulta.tratamento = treatment
            consulta.data = data_e_horario
            consulta.valor = valor
            consulta.metodo_pagamento = metodo_pagamento
            db.commit()


def listar_consultas_data(data):
    with get_db() as db:
        inicio = datetime.strptime(data, "%Y-%m-%d")
        fim = inicio + timedelta(days=1)
        return (
            db.query(Consulta)
            .filter(Consulta.data >= inicio, Consulta.data < fim)
            .order_by(Consulta.data.asc())
            .all()
        )


def listar_consultas_com_paciente_por_data(data_selecionada):
    with get_db() as db:
        inicio = datetime.strptime(data_selecionada, "%Y-%m-%d")
        fim = inicio + timedelta(days=1)
        resultados = (
            db.query(Consulta, Paciente)
            .join(Paciente, Consulta.paciente_id == Paciente.id)
            .filter(
                Consulta.data >= inicio,
                Consulta.data < fim,
                Consulta.compareceu.in_([0, 1]),
            )
            .order_by(Consulta.data.asc())
            .all()
        )
        return [
            {
                "consulta_id": c.id,
                "data": c.data,
                "tratamento": c.tratamento,
                "valor": c.valor,
                "metodo_pagamento": c.metodo_pagamento,
                "compareceu": c.compareceu,
                "paciente_id": p.id,
                "nome": p.nome,
            }
            for c, p in resultados
        ]


def listar_consultas_paciente(paciente_id):
    with get_db() as db:
        return (
            db.query(Consulta)
            .filter(Consulta.paciente_id == paciente_id)
            .order_by(Consulta.data.desc())
            .all()
        )


def listar_faltas_data(data):
    with get_db() as db:
        inicio = datetime.strptime(data, "%Y-%m-%d")
        fim = inicio + timedelta(days=1)
        resultados = (
            db.query(Paciente, Consulta)
            .join(Consulta, Consulta.paciente_id == Paciente.id)
            .filter(
                Consulta.compareceu == 2,
                Consulta.data >= inicio,
                Consulta.data < fim,
            )
            .order_by(Consulta.data.desc())
            .all()
        )
        return [
            {
                "nome": p.nome,
                "tratamento": c.tratamento,
                "data": c.data,
                "id_consulta": c.id,
                "id_paciente": c.paciente_id,
            }
            for p, c in resultados
        ]


def marcar_comparecimento(consulta_id, status=1):
    with get_db() as db:
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        if consulta:
            consulta.compareceu = status
            db.commit()


def marcar_pagamento(consulta_id, pago):
    with get_db() as db:
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        if consulta:
            consulta.pago = pago
            db.commit()


def listar_tratamentos():
    with get_db() as db:
        return db.query(Tratamento).order_by(Tratamento.nome).all()
