from datetime import datetime, timedelta

from .connection import get_db
from .contexto import usuario_id_obrigatorio
from .models import Consulta, Orcamento, Paciente, Tratamento


def _filtro_usuario():
    return Consulta.usuario_id == usuario_id_obrigatorio()


def criar_consulta(paciente_id, treatment, data_e_horario, valor, metodo_pagamento, compareceu=0, duracao=30):
    with get_db() as db:
        consulta = Consulta(
            paciente_id=paciente_id,
            tratamento=treatment,
            data=data_e_horario,
            valor=valor,
            metodo_pagamento=metodo_pagamento,
            compareceu=compareceu,
            duracao=duracao,
            usuario_id=usuario_id_obrigatorio(),
        )
        db.add(consulta)
        db.commit()
        db.refresh(consulta)
        return consulta.id


def buscar_consulta_por_id(consulta_id):
    with get_db() as db:
        return db.query(Consulta).filter(Consulta.id == consulta_id, _filtro_usuario()).first()


def buscar_consulta_por_id_dict(consulta_id):
    with get_db() as db:
        consulta = (
            db.query(Consulta).filter(Consulta.id == consulta_id, _filtro_usuario()).first()
        )
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
            "duracao": consulta.duracao,
        }


def buscar_consulta_Atual(data_e_horario):
    with get_db() as db:
        uid = usuario_id_obrigatorio()
        consulta = (
            db.query(Consulta, Paciente)
            .join(Paciente, Consulta.paciente_id == Paciente.id)
            .filter(
                Consulta.data == data_e_horario,
                Consulta.compareceu == 0,
                Consulta.usuario_id == uid,
            )
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
        uid = usuario_id_obrigatorio()
        db.query(Orcamento).filter(
            Orcamento.consulta_id == consulta_id, Orcamento.usuario_id == uid
        ).delete()
        consulta = (
            db.query(Consulta)
            .filter(Consulta.id == consulta_id, Consulta.usuario_id == uid)
            .first()
        )
        if consulta:
            db.delete(consulta)
        db.commit()


def update_consulta(consulta_id, treatment, data_e_horario, valor, metodo_pagamento, duracao=None):
    with get_db() as db:
        consulta = (
            db.query(Consulta).filter(Consulta.id == consulta_id, _filtro_usuario()).first()
        )
        if consulta:
            consulta.tratamento = treatment
            consulta.data = data_e_horario
            consulta.valor = valor
            consulta.metodo_pagamento = metodo_pagamento
            if duracao is not None:
                consulta.duracao = duracao
            db.commit()


def listar_consultas_data(data):
    with get_db() as db:
        inicio = datetime.strptime(data, "%Y-%m-%d")
        fim = inicio + timedelta(days=1)
        return (
            db.query(Consulta)
            .filter(
                Consulta.data >= inicio,
                Consulta.data < fim,
                _filtro_usuario(),
            )
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
                _filtro_usuario(),
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
                "duracao": c.duracao,
                "paciente_id": p.id,
                "nome": p.nome,
            }
            for c, p in resultados
        ]


def listar_consultas_com_paciente_por_periodo(data_inicio, data_fim):
    """Busca consultas (com paciente) no intervalo [data_inicio, data_fim) em UMA query.

    Mesma saída de listar_consultas_com_paciente_por_data, mas agrupada em um
    único round-trip — evita N queries na agenda semanal (uma por dia).
    :param data_inicio: datetime (inclusive)
    :param data_fim: datetime (exclusive)
    """
    with get_db() as db:
        resultados = (
            db.query(Consulta, Paciente)
            .join(Paciente, Consulta.paciente_id == Paciente.id)
            .filter(
                Consulta.data >= data_inicio,
                Consulta.data < data_fim,
                Consulta.compareceu.in_([0, 1]),
                _filtro_usuario(),
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
                "duracao": c.duracao,
                "paciente_id": p.id,
                "nome": p.nome,
            }
            for c, p in resultados
        ]


def listar_consultas_paciente(paciente_id):
    with get_db() as db:
        return (
            db.query(Consulta)
            .filter(Consulta.paciente_id == paciente_id, _filtro_usuario())
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
                _filtro_usuario(),
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


def listar_faltas_periodo(data_inicio, dias=5):
    """Faltas de `dias` dias úteis a partir de data_inicio, em UMA query.

    Mesma saída de listar_faltas_data, mas para o período inteiro: cada ida-e-volta
    ao Supabase custa ~1s, então consultar a semana dia a dia deixava a tela lenta.
    """
    with get_db() as db:
        inicio = datetime.strptime(data_inicio, "%Y-%m-%d") if isinstance(data_inicio, str) else data_inicio
        fim = inicio + timedelta(days=dias)
        resultados = (
            db.query(Paciente, Consulta)
            .join(Consulta, Consulta.paciente_id == Paciente.id)
            .filter(
                Consulta.compareceu == 2,
                Consulta.data >= inicio,
                Consulta.data < fim,
                _filtro_usuario(),
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
        consulta = (
            db.query(Consulta).filter(Consulta.id == consulta_id, _filtro_usuario()).first()
        )
        if consulta:
            consulta.compareceu = status
            db.commit()


def marcar_pagamento(consulta_id, pago):
    with get_db() as db:
        consulta = (
            db.query(Consulta).filter(Consulta.id == consulta_id, _filtro_usuario()).first()
        )
        if consulta:
            consulta.pago = pago
            db.commit()


def proxima_consulta(data_agora, dias=60):
    """Retorna a próxima consulta futura ainda não atendida (com nome do paciente).

    Usada no painel da agenda para exibir o tempo restante até o próximo
    atendimento. Considera status ainda "ativos" (agendado / falta remarcada /
    notificação disparada).

    :param data_agora: datetime a partir do qual buscar (normalmente datetime.now()).
    :param dias: janela máxima de busca para frente.
    :return: dict com nome/tratamento/data ou None se não houver próxima.
    """
    fim = data_agora + timedelta(days=dias)
    with get_db() as db:
        resultado = (
            db.query(Consulta, Paciente)
            .join(Paciente, Consulta.paciente_id == Paciente.id)
            .filter(
                Consulta.data >= data_agora,
                Consulta.data < fim,
                Consulta.compareceu.in_([0, 3, 4]),
                _filtro_usuario(),
            )
            .order_by(Consulta.data.asc())
            .first()
        )
        if not resultado:
            return None
        c, p = resultado
        return {
            "consulta_id": c.id,
            "paciente_id": c.paciente_id,
            "nome": p.nome,
            "data": c.data,
            "tratamento": c.tratamento,
        }


def listar_tratamentos():
    with get_db() as db:
        uid = usuario_id_obrigatorio()
        return db.query(Tratamento).filter(Tratamento.usuario_id == uid).order_by(Tratamento.nome).all()
