from datetime import datetime, timedelta

from views.agenda_Semanal import COR_FUNDO, _altura_card, _conflita, _consulta_passou, _escurecer

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


# ==================== _consulta_passou ====================


def test_consulta_passou_usa_fim_da_duracao():
    c = {"data": _dt(8, 0), "duracao": 60}
    assert not _consulta_passou(c, _dt(8, 59))
    assert _consulta_passou(c, _dt(9, 0))  # terminou exatamente às 9:00
    assert _consulta_passou(c, _dt(10, 0))


def test_consulta_passou_sem_duracao_usa_30min():
    c = {"data": _dt(8, 0)}  # sem duracao no dict
    assert not _consulta_passou(c, _dt(8, 29))
    assert _consulta_passou(c, _dt(8, 30))


def test_consulta_passou_ontem():
    assert _consulta_passou({"data": _dt(8, 0), "duracao": 30}, _dt(8, 0) + timedelta(days=1))


# ==================== _escurecer ====================


def _rgb(cor):
    return tuple(int(cor[i : i + 2], 16) for i in (1, 3, 5))


def _lum(cor):
    r, g, b = _rgb(cor)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def test_escurecer_escurece_a_cor():
    base = "#1a73e8"
    escura = _escurecer(base)
    assert escura.startswith("#") and len(escura) == 7
    assert _lum(escura) < _lum(base)


def test_escurecer_puxa_pro_fundo_da_grade():
    base = "#33b679"
    escura = _escurecer(base)
    fundo = COR_FUNDO

    def dist(a, b):
        return sum(abs(x - y) for x, y in zip(_rgb(a), _rgb(b)))

    assert dist(escura, fundo) < dist(base, fundo)


def test_escurecer_cor_igual_ao_fundo_nao_muda():
    assert _escurecer(COR_FUNDO) == COR_FUNDO