import customtkinter as ctk

from database import create_user
from views.helpers import (
    INPUT_BG,
    MUTED,
    TEXT_BORDER,
    aplicar_foco,
    criar_campo_senha,
    criar_layout_acesso,
    rotulo,
)


def mostrar(parent):
    _limpar(parent)

    titulo = ctk.CTkLabel(parent, text="Usuários", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 10))

    descricao = ctk.CTkLabel(
        parent,
        text="Gerencie os acessos ao sistema.",
        font=("Segoe UI", 12),
        text_color=MUTED,
    )
    descricao.pack(pady=(0, 25))

    ctk.CTkButton(
        parent,
        text="➕  Criar Usuário",
        command=lambda: mostrar_criar_usuario(parent, voltar=lambda: mostrar(parent)),
        fg_color="#1f6aa5",
        hover_color="#144870",
        font=("Segoe UI", 13, "bold"),
        height=40,
        width=220,
    ).pack(pady=10)


def mostrar_criar_usuario(parent, voltar=None):
    """Renderiza o formulário 'Criar Usuário' DENTRO de `parent`.

    Monta o layout de acesso (painel de marca + formulário) e renderiza o
    formulário de criação, sem abrir janela.
    :param voltar: função chamada ao cancelar/concluir (ex.: voltar ao login).
    """
    _limpar(parent)
    _, form_area = criar_layout_acesso(parent)
    montar_form_criar_usuario(form_area, voltar=voltar)


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


def _limpar(widget):
    """Destroi os widgets existentes em `widget` (troca de "tela" in-panel)."""
    for child in widget.winfo_children():
        child.destroy()