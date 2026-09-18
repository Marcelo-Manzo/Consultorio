import customtkinter as ctk

from database import create_user
from views.helpers import criar_campo_senha


def mostrar(parent):
    titulo = ctk.CTkLabel(parent, text="Usuários", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 10))

    descricao = ctk.CTkLabel(
        parent,
        text="Gerencie os acessos ao sistema.",
        font=("Segoe UI", 12),
        text_color="#9ca3af",
    )
    descricao.pack(pady=(0, 25))

    ctk.CTkButton(
        parent,
        text="➕  Criar Usuário",
        command=lambda: abrir_criar_usuario(parent),
        fg_color="#1f6aa5",
        hover_color="#144870",
        font=("Segoe UI", 13, "bold"),
        height=40,
        width=220,
    ).pack(pady=10)


def abrir_criar_usuario(parent):
    janela = ctk.CTkToplevel(parent)
    janela.title("Novo Usuário")
    janela.resizable(False, False)
    janela.grab_set()

    largura_janela = 420
    altura_janela = 520
    janela.geometry(f"{largura_janela}x{altura_janela}")

    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = int((largura_tela - largura_janela) / 2)
    pos_y = int((altura_tela - altura_janela) / 2)
    janela.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    frame_formulario = ctk.CTkFrame(
        janela,
        fg_color="#141517",
        border_width=1,
        border_color="#242528",
        corner_radius=12,
    )
    frame_formulario.pack(fill="both", expand=True, padx=25, pady=25)

    ctk.CTkLabel(
        frame_formulario, text="Criar Novo Usuário", font=("Segoe UI", 18, "bold"), text_color="#ffffff"
    ).pack(pady=(25, 20))

    nome_entry = ctk.CTkEntry(
        frame_formulario,
        placeholder_text="Nome",
        fg_color="#2b2b2b",
        height=36,
        corner_radius=8,
    )
    nome_entry.pack(fill="x", padx=30, pady=5)

    email_entry = ctk.CTkEntry(
        frame_formulario,
        placeholder_text="E-mail",
        fg_color="#2b2b2b",
        height=36,
        corner_radius=8,
    )
    email_entry.pack(fill="x", padx=30, pady=5)

    def _campo_senha(placeholder):
        entry = criar_campo_senha(frame_formulario, placeholder)
        entry.pack(fill="x", padx=30, pady=5)
        return entry

    senha_entry = _campo_senha("Senha")
    confirmar_entry = _campo_senha("Confirmar senha")

    resultado_label = ctk.CTkLabel(frame_formulario, text="", font=("Segoe UI", 12))
    resultado_label.pack(pady=(10, 6))

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
            resultado_label.configure(text="❌ Erro ao criar usuário (e-mail já cadastrado?).", text_color="#f87171")
            return

        resultado_label.configure(text="✓ Usuário criado com sucesso!", text_color="#4ade80")
        janela.after(1500, janela.destroy)

    ctk.CTkButton(
        frame_formulario,
        text="Criar Usuário",
        command=criar,
        fg_color="#2b7a3e",
        hover_color="#1e542b",
        font=("Segoe UI", 13, "bold"),
        height=40,
        corner_radius=8,
    ).pack(fill="x", padx=30, pady=(5, 20))