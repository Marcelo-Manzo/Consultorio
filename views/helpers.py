import customtkinter as ctk


def alternar_visibilidade_senha(entry, botao):
    """Mostra/oculta a senha de um CTkEntry e troca o ícone do botão."""
    if entry.cget("show") == "*":
        entry.configure(show="")
        botao.configure(text="🙈")
    else:
        entry.configure(show="*")
        botao.configure(text="👁️")


def criar_campo_senha(
    master,
    placeholder="Senha",
    fg_color="#2b2b2b",
    hover_color="#3a3a3a",
    height=36,
    border_width=0,
    border_color=None,
):
    """Cria um campo de senha com o 'olhinho' posicionado DENTRO do input.

    :return: o CTkEntry criado (o botão do olhinho é filho do próprio entry).
    """
    entry = ctk.CTkEntry(
        master,
        placeholder_text=placeholder,
        show="*",
        fg_color=fg_color,
        height=height,
        corner_radius=8,
        border_width=border_width,
        border_color=border_color,
    )

    btn = ctk.CTkButton(
        entry,
        text="👁️",
        width=28,
        height=26,
        corner_radius=6,
        fg_color=fg_color,
        hover_color=hover_color,
        command=lambda: alternar_visibilidade_senha(entry, btn),
    )
    btn.place(relx=1.0, rely=0.5, anchor="e", x=-4)

    return entry