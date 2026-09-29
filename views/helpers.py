import customtkinter as ctk

# Paleta padrão das telas de acesso (dark)
BG_BRAND = "#0c0d0f"      # painel da marca
BG_FORM = "#121316"       # fundo do formulário
INPUT_BG = "#232529"      # fundo dos campos de texto
INPUT_BORDER = "#33363b"  # borda padrão dos campos
INPUT_FOCUS = "#1f6aa5"   # borda com foco
MUTED = "#8b8f98"         # texto secundário
TEXT_BORDER = "#3a3d42"   # separadores e botões outline


def aplicar_foco(entry):
    """Borda azul ao focar em um CTkEntry (design das telas de acesso)."""
    entry.configure(border_width=1, border_color=INPUT_BORDER)
    entry.bind("<FocusIn>", lambda _e: entry.configure(border_color=INPUT_FOCUS))
    entry.bind("<FocusOut>", lambda _e: entry.configure(border_color=INPUT_BORDER))


def rotulo(master, texto):
    """Rótulo de campo em caixa alta, alinhado à esquerda."""
    return ctk.CTkLabel(
        master,
        text=texto,
        font=("Segoe UI", 11, "bold"),
        text_color="#c9cdd4",
        anchor="w",
    )


def criar_painel_marca(master):
    """Cria e empacota o painel esquerdo de marca (selo, título e recursos).

    Usado pelas telas de login e criar usuário para manter o mesmo design.
    """
    brand = ctk.CTkFrame(master, width=300, fg_color=BG_BRAND, corner_radius=0)
    brand.pack(side="left", fill="y")
    brand.pack_propagate(False)

    ctk.CTkLabel(
        brand, text="Consultório v1.0", font=("Segoe UI", 10), text_color="#5f6369"
    ).pack(side="bottom", pady=(0, 16))

    conteudo = ctk.CTkFrame(brand, fg_color="transparent")
    conteudo.pack(side="top", fill="both", expand=True, padx=28)

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

    return brand


def criar_layout_acesso(master):
    """Monta o layout de acesso (painel de marca + área do formulário).

    O painel de marca fica FIXO na esquerda; o conteúdo trocável é renderizado
    dentro de `form_area`. Retorna (container, form_area).
    """
    container = ctk.CTkFrame(master, fg_color="transparent")
    container.pack(fill="both", expand=True)
    criar_painel_marca(container)
    form_area = ctk.CTkFrame(container, fg_color=BG_FORM, corner_radius=0)
    form_area.pack(side="left", fill="both", expand=True)
    return container, form_area


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