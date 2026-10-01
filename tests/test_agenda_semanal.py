from datetime import datetime, timedelta

from views.agenda_Semanal import (
    COR_FUNDO,
    _altura_card,
    _conflita,
    _consulta_passou,
    _dia_da_celula,
    _dia_para_celula,
    _dias_no_mes,
    _escurecer,
)
from views.scrollbar import faixa_polegar, fracao_por_pixel

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


# ==================== MINI-CALENDÁRIO (grade desenhada em canvas) ====================


def test_dia_para_celula_comeca_na_segunda():
    # 01/09/2026 é uma terça (weekday 1) -> ocupa a coluna 1
    assert _dia_para_celula(1, 1) == (1, 0)


def test_dia_para_celula_vira_a_linha_no_fim_da_semana():
    assert _dia_para_celula(6, 1) == (6, 0)
    assert _dia_para_celula(7, 1) == (0, 1)


def test_dia_da_celula_e_o_inverso_de_dia_para_celula():
    for dia in (1, 5, 7, 8, 14, 27, 31):
        col, linha = _dia_para_celula(dia, 1)
        assert _dia_da_celula(col, linha, 1) == dia


def test_dia_da_celula_antes_do_primeiro_dia_da_zero():
    # célula antes do dia 1 pertence ao mês anterior
    assert _dia_da_celula(0, 0, 1) == 0
    assert _dia_da_celula(0, 0, 0) == 1


def test_dias_no_mes():
    assert _dias_no_mes(2026, 1) == 31
    assert _dias_no_mes(2026, 2) == 28
    assert _dias_no_mes(2028, 2) == 29  # ano bissexto
    assert _dias_no_mes(2026, 4) == 30
    assert _dias_no_mes(2026, 12) == 31


# ==================== SCROLLBAR LEVE ====================


def test_polegar_some_sem_rolagem():
    assert faixa_polegar(0.0, 1.0, 600) is None


def test_polegar_ocupa_a_proporcao_da_visao():
    y0, y1 = faixa_polegar(0.0, 0.5, 600)
    assert (y0, y1) == (0.0, 300.0)


def test_polegar_respeita_o_tamanho_minimo():
    # 1% de 2000px = 20px < mínimo de 26 -> cresce para o mínimo
    y0, y1 = faixa_polegar(0.5, 0.51, 2000)
    assert y1 - y0 == 26
    assert y0 == 1000.0


def test_polegar_nao_sai_dos_limites():
    for primeiro, ultimo in ((0.0, 0.99), (0.99, 1.0), (0.98, 1.0), (0.001, 0.002)):
        y0, y1 = faixa_polegar(primeiro, ultimo, 300)
        assert 0 <= y0 < y1 <= 300


def test_arrastar_o_polegar_o_deixa_onde_soltei():
    # O canvas aplica moveto(fracao) -> visao = fracao * (1 - fração visível).
    # O polegar tem que terminar exatamente onde o mouse soltou.
    altura, tam = 600, 100
    visivel = tam / altura
    for y_centro in (100.0, 300.0, 500.0):
        fracao = fracao_por_pixel(y_centro, altura, tam)
        visao = fracao * (1 - visivel)
        y0, y1 = faixa_polegar(visao, visao + visivel, altura)
        assert abs((y0 + y1) / 2 - y_centro) < 1e-6


def test_arrastar_fora_dos_limites_e_limitado():
    assert fracao_por_pixel(-500, 600, 100) == 0.0
    assert fracao_por_pixel(5000, 600, 100) == 1.0