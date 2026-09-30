from datetime import datetime

from views.agenda_Semanal import _altura_card, _conflita

PX_HORA = 54


def _dt(h, m):
    return datetime(2026, 1, 5, h, m)


# ==================== _conflita ====================


def test_conflito_sobreposicao_total():
    assert _conflita(_dt(8, 0), _dt(9, 0), _dt(8, 30), _dt(9, 30))


def test_conflito_sobreposicao_parcial_entrando():
    assert _conflita(_dt(8, 0), _dt(8, 30), _dt(8, 15), _dt(9, 0))


def test_conflito_sobreposto_dentro():
    assert _conflita(_dt(8, 0), _dt(9, 0), _dt(8, 15), _dt(8, 45))


def test_fim_exato_igual_inicio_ok():
    assert not _conflita(_dt(8, 0), _dt(8, 30), _dt(8, 30), _dt(9, 0))


def test_inicio_exato_igual_fim_ok():
    assert not _conflita(_dt(8, 30), _dt(9, 0), _dt(8, 0), _dt(8, 30))


def test_sem_conflito_espacados():
    assert not _conflita(_dt(8, 0), _dt(8, 30), _dt(9, 0), _dt(9, 30))


def test_conflito_duracao_curta_no_meio():
    assert _conflita(_dt(8, 0), _dt(10, 0), _dt(8, 15), _dt(8, 45))


# ==================== _altura_card ====================


def test_altura_30min():
    assert _altura_card(PX_HORA, 30) == 27.0


def test_altura_60min():
    assert _altura_card(PX_HORA, 60) == 54.0


def test_altura_90min():
    assert _altura_card(PX_HORA, 90) == 81.0


def test_altura_sem_duracao_usa_default_na_view():
    # a view chama _altura_card(px_hora, c.get("duracao") or 30)
    assert _altura_card(PX_HORA, 30) == 27.0


def test_altura_piso_para_duracao_pequena():
    assert _altura_card(PX_HORA, 5) == 14
    assert _altura_card(PX_HORA, 10) == 14
    assert _altura_card(PX_HORA, 15) == 14  # 13.5 < piso
    assert _altura_card(PX_HORA, 20) == 18.0  # 18 >= piso