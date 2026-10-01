from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import customtkinter as ctk
from sqlalchemy.exc import InterfaceError, OperationalError

from database.connection import engine
from database.consultas import buscar_consulta_Atual
from database.contexto import definir_usuario
from database.sessao import carregar_sessao, limpar_sessao
from database.usuarios import get_user_by_id
from views import agenda_Semanal, consultas, debug, faltantes, orcamento, pacientes, tratamentos
from views.login import mostrar as mostrar_login
from views.PopUpComparecimento import mostrar as mostrar_popup_comparecimento

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

executor_banco = ThreadPoolExecutor(max_workers=1)

COR_HEADER = "#202124"
COR_ABA_INATIVA = "#dadce0"
COR_ABA_ATIVA = "#1a73e8"
COR_HOVER_ABA = "#36383c"
COR_MENU = "#292a2d"
COR_BORDA = "#3c4043"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Consultório")
        self.geometry("900x600")
        self.configure(fg_color=COR_HEADER)

        self.logado = False          # sessão ativa? controla header e relógio
        self._relogio_iniciado = False

# ==================== CABEÇALHO (menu ☰ + marca) ====================
        self.header = ctk.CTkFrame(self, height=56, corner_radius=0, fg_color=COR_HEADER)
        self.header.pack_propagate(False)
        self.header.grid_rowconfigure(0, weight=1)

        # Botão "☰" (menu lateral) no topo esquerdo
        marca = ctk.CTkFrame(self.header, fg_color="transparent")
        marca.grid(row=0, column=0, padx=(10, 0))

        self.hamb_btn = ctk.CTkButton(
            marca,
            text="☰",
            width=42,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COR_HOVER_ABA,
            text_color=COR_ABA_INATIVA,
            font=("Segoe UI", 22, "bold"),
            command=self._alternar_menu,
        )
        self.hamb_btn.pack(side="left")

        self.header.grid_columnconfigure(1, weight=1)

        # Faixa de cor alegre na base do cabeçalho
        ctk.CTkFrame(self.header, height=3, corner_radius=0, fg_color=COR_ABA_ATIVA).grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )

        # Menu lateral (deslizante) como filho da RAIZ (sobrepõe as telas)
        self._montar_menu()

        # ==================== ÁREA DE CONTEÚDO ====================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="top", fill="both", expand=True, padx=12, pady=(0, 12))

        self.disparar_popup = mostrar_popup_comparecimento(self)
        # A primeira tela (login ou agenda) é decidida em iniciar()

    def _navegar(self, comando):
        self.limpar_frame()
        comando()

    # ==================== MENU LATERAL (☰) ====================

    MENU_LARGURA = 268

    def _montar_menu(self):
        self.menu_traco = ctk.CTkFrame(
            self, width=self.MENU_LARGURA, height=300, corner_radius=0, fg_color=COR_MENU,
            border_width=1, border_color=COR_BORDA,
        )
        self.menu_traco.pack_propagate(False)
        self._menu_animacao = None

        ctk.CTkLabel(
            self.menu_traco, text="Consultório 🦷", font=("Segoe UI", 14, "bold"), text_color="#e8eaed"
        ).pack(anchor="w", padx=16, pady=(16, 10))

        itens = [
            ("👥  Pacientes", self.mostrar_pacientes),
            ("💰  Orçamento", self.mostrar_orcamento),
            ("💉  Tratamentos", self.mostrar_tratamentos),
            ("📅  Agenda", self.mostrar_agenda_semanal),
            ("👥  Faltantes", self.mostrar_faltantes),
            ("🐞  Debug", self.mostrar_debug),
        ]

        def _item():
            return ctk.CTkButton(
                self.menu_traco,
                font=("Segoe UI", 13, "bold"),
                fg_color="transparent",
                hover_color="#23262b",
                text_color="#e8eaed",
                corner_radius=8,
                height=42,
                anchor="w",
            )

        for texto, comando in itens:
            btn = _item()
            btn.configure(text=texto, command=lambda cmd=comando: self._selecionar_tela(cmd))
            btn.pack(fill="x", padx=10, pady=3)

        # Botão "Sair" fixado na parte de baixo do menu
        btn_sair = _item()
        btn_sair.configure(text="🚪  Sair", command=lambda: self._selecionar_tela(self.sair))
        btn_sair.pack(side="bottom", fill="x", padx=10, pady=12)

        # Clique fora do menu fecha (o menu cobre a tela toda, inclusive o ☰)
        self.bind("<Button-1>", self._clique_fora_menu, add="+")

    def _posicionar_menu(self, x):
        self.menu_traco.configure(width=self.MENU_LARGURA)
        self.menu_traco.place(x=x, y=0, relheight=1.0)

    def _clique_fora_menu(self, event):
        if self.menu_traco.winfo_manager() != "place":
            return
        w = event.widget
        while w is not None:
            if w is self.menu_traco:
                return
            w = getattr(w, "master", None)
        self._fechar_menu()

    def _abrir_menu(self):
        self._cancelar_menu()
        self._posicionar_menu(-self.MENU_LARGURA)
        self.menu_traco.lift()
        self._menu_animacao = self.after(12, lambda: self._animar_menu(1))

    def _animar_menu(self, passo):
        if passo > 8:
            self._posicionar_menu(0)
            self._menu_animacao = None
            return
        x = -self.MENU_LARGURA + self.MENU_LARGURA * passo // 8
        self._posicionar_menu(x)
        self._menu_animacao = self.after(12, lambda: self._animar_menu(passo + 1))

    def _fechar_menu(self, ao_fechar=None):
        if not self.menu_traco.winfo_manager() == "place":
            if ao_fechar:
                ao_fechar()
            return
        self._cancelar_menu()
        self._animar_fechar(8, ao_fechar)

    def _animar_fechar(self, passo, ao_fechar):
        if passo <= 0:
            self.menu_traco.place_forget()
            self._menu_animacao = None
            if ao_fechar:
                ao_fechar()
            return
        x = -self.MENU_LARGURA + self.MENU_LARGURA * passo // 8
        self._posicionar_menu(x)
        self._menu_animacao = self.after(12, lambda: self._animar_fechar(passo - 1, ao_fechar))

    def _cancelar_menu(self):
        if self._menu_animacao:
            try:
                self.after_cancel(self._menu_animacao)
            except Exception:
                pass
            self._menu_animacao = None

    def _alternar_menu(self):
        if self.menu_traco.winfo_manager() == "place":
            self._fechar_menu()
        else:
            self._abrir_menu()

    def _selecionar_tela(self, comando):
        def navegar():
            self.limpar_frame()
            comando()

        self._fechar_menu(ao_fechar=navegar)

    # ==================== SEGUNDO PLANO (RELÓGIO) ====================

    def obter_bloco_horario_atual(self):
        agora = datetime.now()
        minuto_bloco = 0 if agora.minute < 30 else 30
        return datetime(agora.year, agora.month, agora.day, agora.hour, minuto_bloco, 0)

    def verificar_horarios_consultas(self):
        if self.logado:
            bloco_atual = self.obter_bloco_horario_atual()
            executor_banco.submit(self._checar_consulta_no_bloco, bloco_atual)
        self.after(30000, self.verificar_horarios_consultas)

    def _checar_consulta_no_bloco(self, bloco_atual):
        try:
            consulta_no_bloco = buscar_consulta_Atual(bloco_atual)
        except Exception:
            consulta_no_bloco = None

        if consulta_no_bloco and self.logado:
            self.after(0, lambda: self.disparar_popup(consulta_no_bloco["data"]))

    # ==================== GERENCIAMENTO DE TELAS ====================
    def limpar_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _abrir_tela(self, montar):
        """Monta a tela e, se o banco estiver com a conexão morta, renova o pool e tenta de novo.

        O Supabase fecha conexão ociosa e o pool_pre_ping foi desligado (custava uma
        ida-e-volta de ~1s em toda tela). Descobrir a conexão morta no meio da tela
        é ruim, então aqui resolvemos: nova tentativa, sem mexer em nada mais.
        """
        for tentativa in (1, 2):
            self.limpar_frame()
            try:
                montar(self.main_frame)
                return
            except (OperationalError, InterfaceError):
                if tentativa == 2:
                    ctk.messagebox.showerror(
                        "Banco de dados",
                        "Não consegui falar com o banco de dados.\nTente novamente em instantes.",
                    )
                    return
                engine.dispose()

    def mostrar_consultas(self):
        self._abrir_tela(consultas.mostrar)

    def mostrar_pacientes(self):
        self._abrir_tela(pacientes.mostrar)

    def mostrar_agenda_semanal(self):
        self._abrir_tela(agenda_Semanal.mostrar)

    def mostrar_faltantes(self):
        self._abrir_tela(faltantes.mostrar)

    def mostrar_orcamento(self):
        self._abrir_tela(orcamento.mostrar)

    def mostrar_tratamentos(self):
        self._abrir_tela(tratamentos.mostrar)

    def mostrar_debug(self):
        self._abrir_tela(debug.mostrar)

    # ==================== CICLO DE VIDA DA SESSÃO (JANELA ÚNICA) ====================

    def entrar(self, usuario):
        """Autentica e mostra a tela principal.

        A janela raiz NUNCA é destruída: só troca o conteúdo do main_frame.
        """
        definir_usuario(usuario)
        if not self.logado:
            self.logado = True
            self.header.pack(side="top", fill="x", before=self.main_frame)
        self.limpar_frame()
        self._navegar(self.mostrar_agenda_semanal)
        if not self._relogio_iniciado:
            self._relogio_iniciado = True
            self.verificar_horarios_consultas()

    def mostrar_login_tela(self):
        """Mostra a tela de login dentro do App (antes de autenticar)."""
        self.header.pack_forget()
        self.limpar_frame()
        mostrar_login(self.main_frame, on_success=self.entrar)

    def sair(self):
        """Encerra a sessão e volta para o login (janela única, sem destroy da raiz)."""
        self._fechar_menu()
        limpar_sessao()
        definir_usuario(None)
        self.logado = False
        self.header.pack_forget()
        self.mostrar_login_tela()


def iniciar():
    app = App()

    uid = carregar_sessao()
    usuario = get_user_by_id(uid) if uid is not None else None
    if uid is not None and usuario is None:
        limpar_sessao()

    if usuario:
        app.entrar(usuario)
    else:
        app.mostrar_login_tela()

    app.mainloop()


if __name__ == "__main__":
    iniciar()