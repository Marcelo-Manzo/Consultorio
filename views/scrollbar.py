import tkinter as tk

# Scrollbar vertical desenhado à mão em um canvas tk puro.
#
# Existe para substituir o CTkScrollbar na agenda: o _draw() do CTkScrollbar termina com
# update_idletasks(), e como o canvas chama o yscrollcommand a cada mudança de
# scrollregion, cada redraw da grade disparava um flush de idle da tela inteira — que
# redesenhava todos os widgets CTk e deixava o arrasto da janela travado (~0,5s por
# passo). Aqui nada disso acontece: só o polegar é redesenhado, e só quando muda.

LARGURA_PADRAO = 10
RAIO_PADRAO = 5
ALTURA_MIN_POLEGAR = 26


def retangulo_arredondado(canvas, x0, y0, x1, y1, raio, **kwargs):
    """Retângulo de cantos arredondados em um único item de canvas (polígono suave)."""
    raio = max(0.0, min(raio, (x1 - x0) / 2, (y1 - y0) / 2))
    if raio <= 0:
        return canvas.create_rectangle(x0, y0, x1, y1, **kwargs)
    pontos = [
        x0 + raio, y0, x1 - raio, y0,
        x1, y0 + raio, x1, y1 - raio,
        x1 - raio, y1, x0 + raio, y1,
        x0, y1 - raio, x0, y0 + raio,
    ]
    return canvas.create_polygon(pontos, smooth=True, splinesteps=12, **kwargs)


def faixa_polegar(primeiro, ultimo, altura, minimo=ALTURA_MIN_POLEGAR):
    """Posição do polegar (y0, y1) em pixels para a visão [primeiro, ultimo].

    Devolve None quando não há rolagem possível (visão completa). O mínimo garante um
    polegar clicável mesmo com muitas consultas.
    """
    if altura <= 0:
        return None
    if primeiro <= 0.0 and ultimo >= 1.0:
        return None

    y0 = primeiro * altura
    y1 = ultimo * altura
    if y1 - y0 < minimo:
        y0 = max(0.0, min(y0, altura - minimo))
        y1 = min(float(altura), y0 + minimo)
    return y0, y1


def fracao_por_pixel(y_polegar, altura, tam_polegar):
    """Inverte o cálculo: pixel do centro do polegar -> fração de scroll (0.0 a 1.0)."""
    curso = max(1.0, altura - tam_polegar)
    return min(1.0, max(0.0, (y_polegar - tam_polegar / 2) / curso))


class ScrollbarLeve(tk.Frame):
    """Scrollbar vertical minimalista: arrasta o polegar ou clica para trocar de página."""

    def __init__(
        self,
        master,
        command,
        cor_fundo="#2b2d31",
        cor_trilho="#33363c",
        cor_polegar="#5f646d",
        largura=LARGURA_PADRAO,
    ):
        super().__init__(master, bg=cor_fundo, width=largura, highlightthickness=0, bd=0)
        self.pack_propagate(False)
        self._command = command
        self._cor_trilho = cor_trilho
        self._cor_polegar = cor_polegar
        self._primeiro = 0.0
        self._ultimo = 1.0
        self._polegar = None  # (y0, y1) em pixels do trilho
        self._arrasto = None  # deslocamento do dedo em relação ao centro do polegar

        self._canvas = tk.Canvas(self, bg=cor_fundo, highlightthickness=0, bd=0, width=largura)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<B1-Button-1>", self._clique)
        self._canvas.bind("<B1-Motion>", self._arrastar)
        self._canvas.bind("<ButtonRelease-1>", self._soltar)
        self._canvas.bind("<Configure>", lambda _e: self._redesenhar())

    # ---------- API compatível com o yscrollcommand do canvas ----------

    def set(self, primeiro, ultimo):
        """Callback do yscrollcommand: posiciona o polegar (0.0 a 1.0)."""
        self._primeiro = float(primeiro)
        self._ultimo = float(ultimo)
        self._redesenhar()

    def get(self):
        return self._primeiro, self._ultimo

    # ---------- desenho ----------

    def _redesenhar(self):
        canvas = self._canvas
        altura = canvas.winfo_height()
        largura = canvas.winfo_width() or LARGURA_PADRAO
        canvas.delete("tudo")
        self._polegar = None
        if altura < 12:
            return

        margem = max(2, largura // 5)
        retangulo_arredondado(
            canvas, margem, 0, largura - margem, altura, RAIO_PADRAO,
            fill=self._cor_trilho, outline="", tags="tudo",
        )
        # Sem rolagem possível: só o trilho, sem polegar
        faixa = faixa_polegar(self._primeiro, self._ultimo, altura)
        if faixa is None:
            return

        retangulo_arredondado(
            canvas, margem, faixa[0], largura - margem, faixa[1], RAIO_PADRAO,
            fill=self._cor_polegar, outline="", tags="tudo",
        )
        self._polegar = faixa

    # ---------- interação ----------

    def _clique(self, evento):
        altura = self._canvas.winfo_height()
        if self._polegar and self._polegar[0] <= evento.y <= self._polegar[1]:
            self._arrasto = evento.y - (self._polegar[0] + self._polegar[1]) / 2
            return
        self._arrasto = None
        pagina = -1 if evento.y < altura / 2 else 1
        self._command("scroll", pagina, "pages")

    def _arrastar(self, evento):
        if self._arrasto is None or not self._polegar:
            return
        altura = self._canvas.winfo_height()
        tam_polegar = self._polegar[1] - self._polegar[0]
        fracao = fracao_por_pixel(evento.y - self._arrasto, altura, tam_polegar)
        self._command("moveto", fracao)

    def _soltar(self, _evento):
        self._arrasto = None