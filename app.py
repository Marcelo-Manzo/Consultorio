from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import customtkinter as ctk

from database.consultas import buscar_consulta_Atual
from database.contexto import definir_usuario
from database.sessao import carregar_sessao, limpar_sessao
from database.usuarios import get_user_by_id
from views import agenda_Semanal, consultas, debug, faltantes, orcamento, pacientes, usuarios
from views.login import mostrar as mostrar_login
from views.PopUpComparecimento import mostrar as mostrar_popup_comparecimento

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# horarios_padrao = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
executor_banco = ThreadPoolExecutor(max_workers=1)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Consultório")
        self.geometry("900x600")

        self.logado = False          # sessão ativa? controla sidebar e relógio
        self._relogio_iniciado = False

        # Frame lateral com botões de navegação
        # (empacotado só após o login — ver entrar())
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#111214")

        self.titulo = ctk.CTkLabel(self.sidebar, text="Menu", font=("Arial", 20, "bold"))
        self.titulo.pack(pady=20)

        fonte_clean = ("Segoe UI", 14, "bold")

        ctk.CTkButton(
            self.sidebar,
            text="Pacientes",
            font=fonte_clean,
            command=self.mostrar_pacientes,
            width=180,
            fg_color="#002A93",
            hover_color="#070062",
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="agenda",
            font=fonte_clean,
            command=self.mostrar_agenda_semanal,
            width=180,
            fg_color="#002A93",
            hover_color="#070062",
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Faltantes",
            font=fonte_clean,
            command=self.mostrar_faltantes,
            width=180,
            fg_color="#002A93",
            hover_color="#070062",
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Contabilidade",
            font=fonte_clean,
            command=self.mostrar_orcamento,
            width=180,
            fg_color="#002A93",
            hover_color="#070062",
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Debug",
            font=fonte_clean,
            command=self.mostrar_debug,
            width=180,
            fg_color="#361a1a",
            hover_color="#542323",
            text_color="#f87171",
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Sair",
            font=fonte_clean,
            command=self.sair,
            width=180,
            fg_color="#361a1a",
            hover_color="#542323",
            text_color="#f87171",
        ).pack(pady=10)

        # Frame principal onde as telas aparecem
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.disparar_popup = mostrar_popup_comparecimento(self)
        # A primeira tela (login ou agenda) é decidida em iniciar()

    # ==================== SEGUNDO PLANO (RELÓGIO) ====================

    def obter_bloco_horario_atual(self):
        agora = datetime.now()
        # Se os minutos forem menores que 30, o bloco é '00'. Se forem maiores, o bloco é '30'.
        minuto_bloco = 0 if agora.minute < 30 else 30

        # Retorna a data de hoje com a hora atual, mas cravada no bloco (00 ou 30) e SEM segundos
        return datetime(agora.year, agora.month, agora.day, agora.hour, minuto_bloco, 0)

    def verificar_horarios_consultas(self):
        # Sem sessão ativa não consulta o banco, só mantém o loop vivo
        if self.logado:
            # Descobre o bloco de 30 min atual (ex: 2026-07-01 15:30:00)
            bloco_atual = self.obter_bloco_horario_atual()

            # Consulta ao banco em THREAD separada: a busca na nuvem demora ~1s e
            # não pode congelar a interface. Quando terminar, agenda o pop-up
            # (que VOLTA para a thread principal do Tk).
            executor_banco.submit(self._checar_consulta_no_bloco, bloco_atual)

        # Pode rodar a checagem a cada 5 minutos (300000 ms) em vez de 1 minuto!
        self.after(30000, self.verificar_horarios_consultas)

    def _checar_consulta_no_bloco(self, bloco_atual):
        try:
            consulta_no_bloco = buscar_consulta_Atual(bloco_atual)
        except Exception:
            consulta_no_bloco = None

        if consulta_no_bloco and self.logado:
            # after() só pode ser chamado pela thread principal; agendamos aqui.
            self.after(0, lambda: self.disparar_popup(consulta_no_bloco["data"]))

    # ==================== GERENCIAMENTO DE TELAS ====================
    def limpar_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_consultas(self):
        self.limpar_frame()
        consultas.mostrar(self.main_frame)

    def mostrar_pacientes(self):
        self.limpar_frame()
        pacientes.mostrar(self.main_frame)

    def mostrar_agenda_semanal(self):
        self.limpar_frame()
        agenda_Semanal.mostrar(self.main_frame)

    def mostrar_faltantes(self):
        self.limpar_frame()
        faltantes.mostrar(self.main_frame)

    def mostrar_orcamento(self):
            self.limpar_frame()
            orcamento.mostrar(self.main_frame)

    def mostrar_debug(self):
        self.limpar_frame()
        debug.mostrar(self.main_frame)

    def mostrar_usuarios(self):
        self.limpar_frame()
        usuarios.mostrar(self.main_frame)

    # ==================== CICLO DE VIDA DA SESSÃO (JANELA ÚNICA) ====================

    def entrar(self, usuario):
        """Autentica e mostra a tela principal.

        A janela raiz NUNCA é destruída: só troca o conteúdo do main_frame.
        """
        definir_usuario(usuario)
        if not self.logado:
            self.logado = True
            self.sidebar.pack(side="left", fill="y", before=self.main_frame, padx=0, pady=0)
        self.limpar_frame()
        self.mostrar_agenda_semanal()
        if not self._relogio_iniciado:
            self._relogio_iniciado = True
            self.verificar_horarios_consultas()

    def mostrar_login_tela(self):
        """Mostra a tela de login dentro do App (antes de autenticar)."""
        self.limpar_frame()
        mostrar_login(self.main_frame, on_success=self.entrar)

    def sair(self):
        """Encerra a sessão e volta para o login (janela única, sem destroy da raiz)."""
        limpar_sessao()
        definir_usuario(None)
        self.logado = False
        self.sidebar.pack_forget()
        self.mostrar_login_tela()


def iniciar():
    app = App()

    # 1) tenta restaurar a sessao salva no Credential Manager
    uid = carregar_sessao()
    usuario = get_user_by_id(uid) if uid is not None else None
    if uid is not None and usuario is None:
        limpar_sessao()  # usuario nao existe mais -> limpa a sessao

    if usuario:
        app.entrar(usuario)          # sessao valida -> pula o login
    else:
        app.mostrar_login_tela()     # sem sessao -> tela de login

    app.mainloop()


if __name__ == "__main__":
    iniciar()
