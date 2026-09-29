import customtkinter as ctk

from database import create_user, get_user_by_email, validar_senha
from database.sessao import limpar_sessao, salvar_sessao
from views.helpers import (
    INPUT_BG,
    INPUT_BORDER,
    MUTED,
    TEXT_BORDER,
    aplicar_foco,
    criar_campo_senha,
    criar_layout_acesso,
    rotulo,
)


def mostrar(parent, on_success=None):
    """
    Renderiza a tela de login DENTRO de `parent` (janela única do App).

    O painel esquerdo de marca é montado UMA única vez; "Criar Usuário" apenas
    troca o conteúdo do painel direito, mantendo a marca fixa na tela.

    :param parent: container pai (ex.: main_frame do App).
    :param on_success: função chamada com o usuário autenticado (opcional).
                       Ex.: on_success=self.entrar
    """
    _limpar(parent)
    _, form_area = criar_layout_acesso(parent)

    def _mostrar_criar():
        _limpar(form_area)
        montar_form_criar_usuario(form_area, voltar=_mostrar_acesso)

    def _mostrar_acesso():
        _limpar(form_area)

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

        rotulo(form, "E-MAIL").pack(anchor="w", pady=(0, 6))

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
        aplicar_foco(email_entry)

        rotulo(form, "SENHA").pack(anchor="w", pady=(16, 6))

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
        aplicar_foco(senha_entry)

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
            command=_mostrar_criar,
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

    _mostrar_acesso()


def _limpar(widget):
    """Destroi os widgets existentes em `widget` (troca de "tela" in-panel)."""
    for child in widget.winfo_children():
        child.destroy()


def _campo_rotulado(master, rotulo_txt, placeholder):
    rotulo(master, rotulo_txt).pack(anchor="w", pady=(10, 6))
    entry = ctk.CTkEntry(
        master,
        placeholder_text=placeholder,
        fg_color=INPUT_BG,
        height=42,
        corner_radius=8,
    )
    entry.pack(fill="x")
    aplicar_foco(entry)
    return entry


def _campo_senha_rotulado(master, rotulo_txt, placeholder):
    rotulo(master, rotulo_txt).pack(anchor="w", pady=(10, 6))
    entry = criar_campo_senha(
        master,
        placeholder=placeholder,
        fg_color=INPUT_BG,
        hover_color="#2d3035",
        height=42,
    )
    entry.pack(fill="x")
    aplicar_foco(entry)
    return entry


def montar_form_criar_usuario(master, voltar=None):
    """Renderiza o formulário de criação de usuário DENTRO de `master`.

    Não monta container/layout: apenas o formulário. O `master` normalmente é a
    `form_area` do layout de acesso (painel de marca fixo à esquerda).
    """
    form = ctk.CTkFrame(master, fg_color="transparent", width=400)
    form.pack(expand=True)

    selo = ctk.CTkFrame(form, width=64, height=64, corner_radius=32, fg_color="#2b7a3e")
    selo.pack(pady=(0, 12))
    ctk.CTkLabel(selo, text="🦷", font=("Segoe UI", 28), text_color="#ffffff").place(
        relx=0.5, rely=0.5, anchor="center"
    )

    ctk.CTkLabel(
        form, text="Criar Novo Usuário", font=("Segoe UI", 22, "bold"), text_color="#ffffff"
    ).pack()

    ctk.CTkLabel(
        form,
        text="Preencha os dados abaixo para criar um novo acesso.",
        font=("Segoe UI", 12),
        text_color=MUTED,
    ).pack(pady=(4, 8))

    nome_entry = _campo_rotulado(form, "NOME", "Seu nome")
    email_entry = _campo_rotulado(form, "E-MAIL", "seuemail@exemplo.com")
    senha_entry = _campo_senha_rotulado(form, "SENHA", "Crie uma senha")
    confirmar_entry = _campo_senha_rotulado(form, "CONFIRMAR SENHA", "Repita a senha")

    resultado_label = ctk.CTkLabel(form, text="", font=("Segoe UI", 12), height=20)
    resultado_label.pack(pady=(10, 0))

    def criar():
        nome = nome_entry.get().strip()
        email = email_entry.get().strip()
        senha = senha_entry.get()
        confirmar = confirmar_entry.get()

        if not nome or not email or not senha or not confirmar:
            resultado_label.configure(text="❌ Preencha todos os campos.", text_color="#f87171")
            return

        if "@" not in email or "." not in email:
            resultado_label.configure(text="❌ E-mail inválido.", text_color="#f87171")
            return

        if senha != confirmar:
            resultado_label.configure(text="❌ As senhas não coincidem.", text_color="#f87171")
            return

        try:
            create_user(nome, email, senha)
        except Exception:
            resultado_label.configure(
                text="❌ Erro ao criar usuário (e-mail já cadastrado?).", text_color="#f87171"
            )
            return

        resultado_label.configure(text="✓ Usuário criado com sucesso!", text_color="#4ade80")
        if voltar:
            master.after(1500, voltar)

    ctk.CTkButton(
        form,
        text="Criar Usuário",
        command=criar,
        fg_color="#2b7a3e",
        hover_color="#1e542b",
        font=("Segoe UI", 14, "bold"),
        height=42,
        corner_radius=8,
    ).pack(fill="x", pady=(6, 6))

    ctk.CTkButton(
        form,
        text="Voltar",
        command=voltar if voltar else lambda: None,
        fg_color="transparent",
        hover_color="#1c1e22",
        border_width=1,
        border_color=TEXT_BORDER,
        text_color="#c9cdd4",
        font=("Segoe UI", 13, "bold"),
        height=42,
        corner_radius=8,
    ).pack(fill="x", pady=(0, 10))

    nome_entry.focus_set()