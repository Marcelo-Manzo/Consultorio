import customtkinter as ctk

from database.consultas import listar_tratamentos
from database.tratamentos import (
    create_tratamento,
    deletar_tratamento,
    update_tratamento,
)


def _parse_valor(texto):
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if not texto:
        return None
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def _fmt_valor(valor):
    if valor is None:
        return "—"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_duracao(duracao):
    if duracao is None:
        return "⏱ não definida"
    return f"⏱ {duracao} min"


def mostrar(parent):
    # =========================================================================
    # MODAL ÚNICO DE TRATAMENTO (CRIAÇÃO E EDIÇÃO)
    # =========================================================================
    def abrir_modal_tratamento(tratamento=None):
        eh_edicao = tratamento is not None

        pop_up = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        pop_up.title("Editar Tratamento" if eh_edicao else "Novo Tratamento")

        largura_janela, altura_janela = 400, 400
        largura_tela = pop_up.winfo_screenwidth()
        altura_tela = pop_up.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        pop_up.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        pop_up.grab_set()

        ctk.CTkLabel(
            pop_up,
            text="Editar Tratamento" if eh_edicao else "Cadastrar Novo Tratamento",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
        ).pack(pady=(20, 15))

        nome_entry = ctk.CTkEntry(pop_up, width=280, height=35, placeholder_text="Nome do tratamento", fg_color="#2b2b2b")
        nome_entry.pack(pady=6)

        valor_entry = ctk.CTkEntry(pop_up, width=280, height=35, placeholder_text="Valor (R$)", fg_color="#2b2b2b")
        valor_entry.pack(pady=6)

        duracao_entry = ctk.CTkEntry(
            pop_up, width=280, height=35, placeholder_text="Duração em minutos (opcional)", fg_color="#2b2b2b"
        )
        duracao_entry.pack(pady=6)

        if eh_edicao:
            nome_entry.insert(0, tratamento.nome or "")
            valor_entry.insert(0, _fmt_valor(tratamento.valor))
            if tratamento.duracao is not None:
                duracao_entry.insert(0, str(tratamento.duracao))

        resultado_label = ctk.CTkLabel(pop_up, text="", font=("Segoe UI", 12))
        resultado_label.pack(pady=(5, 0))

        def salvar():
            nome = nome_entry.get().strip()
            if not nome:
                resultado_label.configure(text="❌ Insira um nome", text_color="#f87171")
                return

            valor = _parse_valor(valor_entry.get())
            if valor is None:
                resultado_label.configure(text="❌ Valor inválido", text_color="#f87171")
                return

            duracao = None
            duracao_texto = duracao_entry.get().strip()
            if duracao_texto:
                if not duracao_texto.isdigit() or int(duracao_texto) <= 0:
                    resultado_label.configure(text="❌ Duração inválida (minutos inteiros)", text_color="#f87171")
                    return
                duracao = int(duracao_texto)

            try:
                if eh_edicao:
                    update_tratamento(tratamento.id, nome, valor, duracao)
                else:
                    create_tratamento(nome, valor, duracao)
            except Exception as e:
                resultado_label.configure(text=f"❌ Erro ao salvar: {e}", text_color="#f87171")
                return

            atualizar_lista()
            pop_up.destroy()

        ctk.CTkButton(
            pop_up,
            text="Atualizar Tratamento" if eh_edicao else "Salvar Tratamento",
            command=salvar,
            width=280,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color="#2b7a3e",
            hover_color="#1e542b",
        ).pack(pady=(20, 10))

    def excluir_tratamento(tratamento_id):
        try:
            deletar_tratamento(tratamento_id)
            atualizar_lista()
        except Exception as e:
            resultado_label_busca.configure(text=f"❌ Erro ao excluir: {e}", text_color="#f87171")

    # =========================================================================
    # TELA PRINCIPAL (LISTAGEM E GESTÃO)
    # =========================================================================
    lbl_titulo = ctk.CTkLabel(parent, text="Controle de Tratamentos", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    lbl_titulo.pack(anchor="w", padx=25, pady=(20, 10))

    frame_topo = ctk.CTkFrame(parent, fg_color="#141517", border_width=1, border_color="#242528")
    frame_topo.pack(fill="x", padx=25, pady=(0, 15))

    ctk.CTkLabel(
        frame_topo,
        text="Duração definida aqui é usada como padrão ao agendar uma consulta deste tratamento.",
        font=("Segoe UI", 12),
        text_color="#9ca3af",
    ).pack(side="left", padx=15, pady=12)

    btn_novo_tratamento = ctk.CTkButton(
        frame_topo,
        text="+ Criar Tratamento",
        height=40,
        font=("Segoe UI", 13, "bold"),
        fg_color="#08631d",
        hover_color="#073c14",
        command=lambda: abrir_modal_tratamento(),
    )
    btn_novo_tratamento.pack(side="right", padx=(0, 15), pady=12)

    frame_container_lista = ctk.CTkFrame(parent, fg_color="#141517", border_width=1, border_color="#242528")
    frame_container_lista.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    resultado_label_busca = ctk.CTkLabel(
        frame_container_lista, text="Listando todos os tratamentos", font=("Segoe UI", 12), text_color="#9ca3af"
    )
    resultado_label_busca.pack(anchor="w", padx=15, pady=(10, 5))

    lista_frame = ctk.CTkScrollableFrame(frame_container_lista, fg_color="transparent")
    lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def atualizar_lista():
        for widget in lista_frame.winfo_children():
            widget.destroy()

        try:
            tratamentos = listar_tratamentos()
        except Exception as e:
            resultado_label_busca.configure(text=f"❌ Erro ao buscar tratamentos: {e}", text_color="#f87171")
            return

        if not tratamentos:
            resultado_label_busca.configure(text="❌ Nenhum tratamento cadastrado.", text_color="#f87171")

            frame_vazio = ctk.CTkFrame(lista_frame, fg_color="transparent")
            frame_vazio.pack(pady=30)
            ctk.CTkLabel(
                frame_vazio,
                text="Nenhum tratamento cadastrado. Clique em \"+ Criar Tratamento\" para começar.",
                font=("Segoe UI", 12, "italic"),
                text_color="#6b7280",
            ).pack()
            return

        resultado_label_busca.configure(text=f"✓ Exibindo {len(tratamentos)} tratamento(s).", text_color="#9ca3af")

        for t in tratamentos:
            card = ctk.CTkFrame(
                lista_frame, fg_color="#25262b", border_width=1, border_color="#333438", corner_radius=8
            )
            card.pack(fill="x", padx=5, pady=4)

            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            lbl_nome = ctk.CTkLabel(
                frame_info, text=f"🦷 {t.nome}", font=("Segoe UI", 13, "bold"), text_color="#e5e7eb"
            )
            lbl_nome.pack(anchor="w")

            lbl_dur = ctk.CTkLabel(frame_info, text=_fmt_duracao(t.duracao), font=("Segoe UI", 11), text_color="#9ca3af")
            lbl_dur.pack(anchor="w", pady=(2, 0))

            frame_valor = ctk.CTkFrame(card, fg_color="transparent")
            frame_valor.pack(side="right", anchor="e", padx=12, pady=10)

            ctk.CTkLabel(
                frame_valor,
                text=_fmt_valor(t.valor),
                font=("Segoe UI", 13, "bold"),
                text_color="#4ade80",
            ).pack(anchor="e")

            frame_acoes = ctk.CTkFrame(card, fg_color="transparent")
            frame_acoes.pack(side="right", padx=10, pady=10)

            btn_editar = ctk.CTkButton(
                frame_acoes,
                text="Editar",
                command=lambda tratamento_obj=t: abrir_modal_tratamento(tratamento_obj),
                width=60,
                height=28,
                font=("Segoe UI", 11, "bold"),
                corner_radius=5,
                fg_color="#1e293b",
                hover_color="#334155",
                text_color="#60a5fa",
            )
            btn_editar.pack(side="left", padx=3)

            btn_excluir = ctk.CTkButton(
                frame_acoes,
                text="❌",
                command=lambda id_t=t.id: excluir_tratamento(id_t),
                width=28,
                height=28,
                corner_radius=5,
                fg_color="#361a1a",
                hover_color="#542323",
                text_color="#f87171",
            )
            btn_excluir.pack(side="left", padx=3)

    atualizar_lista()