import customtkinter as ctk

from database import get_user_by_email, validar_senha
from database.sessao import limpar_sessao, salvar_sessao
from views.helpers import criar_campo_senha
from views.usuarios import abrir_criar_usuario

# Paleta da tela de login (dark)
BG_BRAND = "#0c0d0f"          # painel esquerdo (marca)
BG_FORM = "#121316"           # painel direito (formulário)
INPUT_BG = "#232529"          # fundo dos campos
INPUT_BORDER = "#33363b"      # borda padrão dos campos
INPUT_FOCUS = "#1f6aa5"       # borda com foco
MUTED = "#8b8f98"             # texto secundário
TEXT_BORDER = "#3a3d42"       # botões outline


def _campo(entry):
    """Aplica a borda de foco/desfoco em um CTkEntry."""
    entry.configure(border_width=1, border_color=INPUT_BORDER)

    def focar(_e):
        entry.configure(border_color=INPUT_FOCUS)

    def desfocar(_e):
        entry.configure(border_color=INPUT_BORDER)

    entry.bind("<FocusIn>", focar)
    entry.bind("<FocusOut>", desfocar)


def _rotulo(master, texto):
    return ctk.CTkLabel(
        master,
        text=texto,
        font=("Segoe UI", 11, "bold"),
        text_color="#c9cdd4",
        anchor="w",
    )


def mostrar(parent, on_success=None):
    """
    Renderiza a tela de login DENTRO de `parent` (janela única do App).

    Layout em dois painéis:
      [marca]  painel escuro com logo/tagline à esquerda
      [form]   formulário de acesso centralizado à direita

    :param parent: container pai (ex.: main_frame do App).
    :param on_success: função chamada com o usuário autenticado (opcional).
                       Ex.: on_success=self.entrar
    """
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="both", expand=True)

    # ---------- Painel esquerdo: marca ----------
    brand = ctk.CTkFrame(container, width=300, fg_color=BG_BRAND, corner_radius=0)
    brand.pack(side="left", fill="y")
    brand.pack_propagate(False)

    ctk.CTkLabel(
        brand, text="Consultório v1.0", font=("Segoe UI", 10), text_color="#5f6369"
    ).pack(side="bottom", pady=(0, 16))

    conteudo = ctk.CTkFrame(brand, fg_color="transparent")
    conteudo.pack(side="top", fill="both", expand=True, padx=28)

    # Selo redondo com o "dente"
    selo = ctk.CTkFrame(
        conteudo, width=68, height=68, corner_radius=34, fg_color="#1f6aa5"
    )
    selo.pack(pady=(46, 18))
    ctk.CTkLabel(
        selo, text="🦷", font=("Segoe UI", 30), text_color="#ffffff"
    ).place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(
        conteudo,
        text="Consultório",
        font=("Segoe UI", 26, "bold"),
        text_color="#ffffff",
    ).pack(anchor="w")

    ctk.CTkLabel(
        conteudo,
        text="A gestão completa do seu consultório\nodontológico em um só lugar.",
        font=("Segoe UI", 12),
        text_color=MUTED,
        justify="left",
        anchor="w",
    ).pack(anchor="w", pady=(6, 26))

    barra = ctk.CTkFrame(conteudo, width=3, height=54, fg_color="#1f6aa5", corner_radius=2)
    barra.pack(side="left", pady=(0, 8))
    barra.pack_propagate(False)

    recursos = ctk.CTkFrame(conteudo, fg_color="transparent")
    recursos.pack(side="left", fill="y", padx=(12, 0))
    for texto in ("Agenda e consultas", "Pacientes e orçamentos", "Controle de faltantes"):
        ctk.CTkLabel(
            recursos, text="•  " + texto, font=("Segoe UI", 12), text_color="#b6bac1"
        ).pack(anchor="w", pady=3)

    # ---------- Painel direito: formulário ----------
    form_area = ctk.CTkFrame(container, fg_color=BG_FORM, corner_radius=0)
    form_area.pack(side="left", fill="both", expand=True)

    form = ctk.CTkFrame(form_area, fg_color="transparent", width=370)
    form.pack(expand=True)

    ctk.CTkLabel(
        form, text="Bem-vindo de volta 👋", font=("Segoe UI", 22, "bold"), text_color="#ffffff"
    ).pack(anchor="w")

    ctk.CTkLabel(
        form,
        text="Acesse com seu e-mail e senha para continuar.",
        font=("Segoe UI", 12),
        text_color=MUTED,
        anchor="w",
    ).pack(anchor="w", pady=(4, 24))

    e_label = _rotulo(form, "E-MAIL")
    e_label.pack(anchor="w", pady=(0, 6))

    email_entry = ctk.CTkEntry(
        form,
        placeholder_text="seuemail@exemplo.com",
        fg_color=INPUT_BG,
        height=42,
        corner_radius=8,
        border_width=1,
        border_color=INPUT_BORDER,
    )
    email_entry.pack(fill="x")
    _campo(email_entry)

    _rotulo(form, "SENHA").pack(anchor="w", pady=(16, 6))

    senha_entry = criar_campo_senha(
        form,
        placeholder="Sua senha",
        fg_color=INPUT_BG,
        hover_color="#2d3035",
        height=42,
        border_width=1,
        border_color=INPUT_BORDER,
    )
    senha_entry.pack(fill="x")
    _campo(senha_entry)

    frame_opcoes = ctk.CTkFrame(form, fg_color="transparent")
    frame_opcoes.pack(fill="x", pady=(14, 0))

    chk_manter = ctk.CTkCheckBox(
        frame_opcoes,
        text="Manter conectado",
        font=("Segoe UI", 12),
        fg_color="#1f6aa5",
        hover_color="#144870",
        text_color="#c9cdd4",
    )
    chk_manter.pack(side="left")
    chk_manter.select()   # vem MARCADO por padrao

    resultado_label = ctk.CTkLabel(form, text="", font=("Segoe UI", 12), height=20)
    resultado_label.pack(pady=(12, 0))

    def tentar_login(_event=None):
        email = email_entry.get().strip()
        senha = senha_entry.get()

        if not email or not senha:
            resultado_label.configure(text="❌ Preencha e-mail e senha.", text_color="#f87171")
            return

        try:
            usuario = get_user_by_email(email)
        except Exception:
            resultado_label.configure(text="❌ Erro ao acessar o banco.", text_color="#f87171")
            return

        if not usuario:
            resultado_label.configure(text="❌ Usuário não encontrado.", text_color="#f87171")
            return

        if not validar_senha(senha, usuario.senha_hash):
            resultado_label.configure(text="❌ Senha incorreta.", text_color="#f87171")
            return

        resultado_label.configure(text="✓ Entrando...", text_color="#4ade80")
        if on_success:
            if chk_manter.get():
                salvar_sessao(usuario.id)
            else:
                limpar_sessao()
            on_success(usuario)

    ctk.CTkButton(
        form,
        text="Entrar",
        command=tentar_login,
        fg_color="#1f6aa5",
        hover_color="#144870",
        font=("Segoe UI", 14, "bold"),
        height=42,
        corner_radius=8,
    ).pack(fill="x", pady=(4, 6))

    # Divisor "ou"
    div = ctk.CTkFrame(form, fg_color="transparent")
    div.pack(fill="x", pady=(8, 14))
    ctk.CTkFrame(div, height=1, fg_color=TEXT_BORDER, corner_radius=0).pack(
        side="left", fill="x", expand=True, pady=6
    )
    ctk.CTkLabel(div, text="  ou  ", font=("Segoe UI", 11), text_color=MUTED).pack(side="left")
    ctk.CTkFrame(div, height=1, fg_color=TEXT_BORDER, corner_radius=0).pack(
        side="left", fill="x", expand=True, pady=6
    )

    ctk.CTkButton(
        form,
        text="Criar Usuário",
        command=lambda: abrir_criar_usuario(parent),
        fg_color="transparent",
        hover_color="#1c1e22",
        border_width=1,
        border_color=TEXT_BORDER,
        text_color="#c9cdd4",
        font=("Segoe UI", 13, "bold"),
        height=42,
        corner_radius=8,
    ).pack(fill="x")

    email_entry.bind("<Return>", tentar_login)
    senha_entry.bind("<Return>", tentar_login)

    email_entry.focus_set()