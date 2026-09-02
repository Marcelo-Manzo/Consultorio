from datetime import datetime, timedelta

from sqlalchemy import func

from .connection import get_db
from .models import Consulta, Orcamento, Paciente


def criar_orcamento(consulta_id, paciente_id, valor, metodo, data_criacao, status=0):
    with get_db() as db:
        orcamento = Orcamento(
            consulta_id=consulta_id,
            paciente_id=paciente_id,
            valor=valor,
            forma_pagamento=metodo,
            status=status,
            data_criacao=data_criacao,
        )
        db.add(orcamento)
        db.commit()


def update_orcamento_por_consulta(consulta_id, paciente_id, valor, forma_pagamento, status=0):
    with get_db() as db:
        orcamento = (
            db.query(Orcamento).filter(Orcamento.consulta_id == consulta_id).first()
        )
        if orcamento:
            orcamento.paciente_id = paciente_id
            orcamento.valor = valor
            orcamento.forma_pagamento = forma_pagamento
            orcamento.status = status
            db.commit()


def _inicio_fim_mes(mes, ano):
    """Retorna (inicio, fim) do mês/ano como datetime.
    Usa faixa [inicio, fim) para filtrar por mês de forma compatível com SQL Server
    (func.extract não é suportado pelo SQL Server)."""
    inicio = datetime(ano, mes, 1)
    if mes == 12:
        fim = datetime(ano + 1, 1, 1)
    else:
        fim = datetime(ano, mes + 1, 1)
    return inicio, fim


def listar_orcamentos_por_mes(mes, ano):
    inicio, fim = _inicio_fim_mes(mes, ano)
    with get_db() as db:
        resultados = (
            db.query(Orcamento, Paciente)
            .join(Paciente, Orcamento.paciente_id == Paciente.id)
            .filter(Orcamento.data_criacao >= inicio, Orcamento.data_criacao < fim)
            .order_by(Orcamento.data_criacao.desc())
            .all()
        )
        return [
            {
                "id": o.id,
                "consulta_id": o.consulta_id,
                "paciente_id": o.paciente_id,
                "paciente_nome": p.nome,
                "valor": o.valor,
                "forma_pagamento": o.forma_pagamento,
                "status": o.status,
                "data_criacao": o.data_criacao,
            }
            for o, p in resultados
        ]


def atualizar_status_orcamento(orcamento_id, novo_status):
    with get_db() as db:
        orcamento = db.query(Orcamento).filter(Orcamento.id == orcamento_id).first()
        if orcamento:
            orcamento.status = novo_status
            db.commit()


def obter_ganho_total_mes(mes, ano):
    inicio, fim = _inicio_fim_mes(mes, ano)
    with get_db() as db:
        total = (
            db.query(func.coalesce(func.sum(Orcamento.valor), 0))
            .filter(
                Orcamento.status == 1,
                Orcamento.data_criacao >= inicio,
                Orcamento.data_criacao < fim,
            )
            .scalar()
        )
        return total


def lista_orcamentos_por_status_data(status, data_inicio, data_fim):
    with get_db() as db:
        query = db.query(Orcamento, Paciente).join(
            Paciente, Orcamento.paciente_id == Paciente.id
        )

        if status is not None and str(status).isdigit():
            query = query.filter(Orcamento.status == int(status))

        if data_inicio:
            inicio = data_inicio if isinstance(data_inicio, datetime) else datetime.strptime(data_inicio, "%d/%m/%Y")
            query = query.filter(Orcamento.data_criacao >= inicio)

        if data_fim:
            fim = data_fim if isinstance(data_fim, datetime) else datetime.strptime(data_fim, "%d/%m/%Y")
            fim = fim + timedelta(days=1)
            query = query.filter(Orcamento.data_criacao < fim)

        resultados = query.order_by(Orcamento.data_criacao.desc()).all()

        return [
            {
                "id": o.id,
                "consulta_id": o.consulta_id,
                "paciente_id": o.paciente_id,
                "paciente_nome": p.nome,
                "paciente_cpf": p.cpf,
                "valor": o.valor,
                "forma_pagamento": o.forma_pagamento,
                "status": o.status,
                "data_criacao": o.data_criacao,
            }
            for o, p in resultados
        ]


def buscar_orcamento_por_id_consulta(id_consulta):
    with get_db() as db:
        resultados = (
            db.query(Orcamento)
            .join(Consulta, Orcamento.consulta_id == Consulta.id)
            .filter(Consulta.id == id_consulta)
            .all()
        )
        return [{"id": o.id} for o in resultados]


def deletar_orcamento(orcamento_id):
    with get_db() as db:
        orcamento = db.query(Orcamento).filter(Orcamento.id == orcamento_id).first()
        if orcamento:
            db.delete(orcamento)
            db.commit()
