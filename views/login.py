import customtkinter as ctk

from database import get_user_by_email, validar_senha


def mostrar(on_success=None):
    """
    Cria a janela de login.

    :param on_success: função chamada com o usuário autenticado (opcional).
                       Ex.: on_success=lambda usuario: abrir_app(usuario)
    :return: a janela (ctk.CTk) criada. Chame .mainloop() nela.
    """
    janela = ctk.CTk()
    janela.title("Consultório — Login")
    janela.geometry("420x480")
    janela.resizable(False, False)

    # Centraliza a janela na tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = int((largura_tela - 420) / 2)
    pos_y = int((altura_tela - 480) / 2)
    janela.geometry(f"420x480+{pos_x}+{pos_y}")

    frame_login = ctk.CTkFrame(
        janela,
        fg_color="#141517",
        border_width=1,
        border_color="#242528",
        corner_radius=12,
    )
    frame_login.pack(fill="both", expand=True, padx=30, pady=30)

    ctk.CTkLabel(
        frame_login, text="🦷 Consultório", font=("Segoe UI", 24, "bold"), text_color="#ffffff"
    ).pack(pady=(30, 5))

    ctk.CTkLabel(
        frame_login,
        text="Acesse com seu e-mail e senha",
        font=("Segoe UI", 12),
        text_color="#9ca3af",
    ).pack(pady=(0, 25))

    email_entry = ctk.CTkEntry(
        frame_login,
        placeholder_text="E-mail",
        fg_color="#2b2b2b",
        height=38,
        corner_radius=8,
    )
    email_entry.pack(fill="x", padx=30, pady=5)

    senha_entry = ctk.CTkEntry(
        frame_login,
        placeholder_text="Senha",
        show="*",
        fg_color="#2b2b2b",
        height=38,
        corner_radius=8,
    )
    senha_entry.pack(fill="x", padx=30, pady=5)

    resultado_label = ctk.CTkLabel(frame_login, text="", font=("Segoe UI", 12))
    resultado_label.pack(pady=(10, 5))

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
            on_success(usuario)

    ctk.CTkButton(
        frame_login,
        text="Entrar",
        command=tentar_login,
        fg_color="#1f6aa5",
        hover_color="#144870",
        font=("Segoe UI", 14, "bold"),
        height=40,
        corner_radius=8,
    ).pack(fill="x", padx=30, pady=(5, 15))

    email_entry.bind("<Return>", tentar_login)
    senha_entry.bind("<Return>", tentar_login)

    email_entry.focus_set()
    return janela