import calendar
from datetime import datetime
import customtkinter as ctk
from database.models import lista_orcamentos_por_status_data

controle_mensal = {"deslocamento": 0}


def mostrar(parent):
    # Limpa o container atual antes de renderizar
    for widget in parent.winfo_children():
        widget.destroy()

    def exportar_em_excel():
        """Exporta os dados filtrados para uma planilha Excel."""
        pass

    def exportar_em_pdf():
        """Gera um relatório em PDF com os dados filtrados."""
        pass

    def on_aprovar_click(orcamento_id):
        """Atualiza o status do orçamento para Aprovado (1) no banco de dados."""
        print(f"Aprovar orçamento: {orcamento_id}")

    def on_cancelar_click(orcamento_id):
        """Atualiza o status do orçamento para Cancelado (2) no banco de dados."""
        print(f"Cancelar orçamento: {orcamento_id}")

    def atualizar_orcamento():
        # Layout Principal
        parent.grid_rowconfigure(0, weight=0)  # Cards
        parent.grid_rowconfigure(1, weight=0)  # Filtros
        parent.grid_rowconfigure(2, weight=1)  # Tabela
        parent.grid_columnconfigure(0, weight=1)

        # =========================================================================
        # 1. CARDS DE RESUMO FINANCEIRO
        # =========================================================================
        frame_cards = ctk.CTkFrame(parent, fg_color="transparent")
        frame_cards.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        frame_cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        dados_cards = [
            {"status_id": 0, "titulo": "PENDENTES", "cor": "#E6A100", "bg_subtil": "#2a2415"},
            {"status_id": 1, "titulo": "APROVADOS", "cor": "#2FA572", "bg_subtil": "#162820"},
            {"status_id": 2, "titulo": "CANCELADOS", "cor": "#EA4335", "bg_subtil": "#2b1919"},
        ]

        dict_cards_ui = {}

        for col, card in enumerate(dados_cards):
            status_id = card["status_id"]
            fundo_card = ctk.CTkFrame(
                frame_cards,
                fg_color="#1e1f22",
                border_width=1,
                border_color="#2b2d31",
                corner_radius=10,
            )
            fundo_card.grid(row=0, column=col, padx=6, pady=5, sticky="ew")

            ctk.CTkFrame(fundo_card, fg_color=card["cor"], height=3, corner_radius=0).pack(fill="x", side="top")

            conteudo = ctk.CTkFrame(fundo_card, fg_color="transparent")
            conteudo.pack(fill="both", expand=True, padx=15, pady=12)

            header_card = ctk.CTkFrame(conteudo, fg_color="transparent")
            header_card.pack(fill="x")

            ctk.CTkLabel(
                header_card,
                text=card["titulo"],
                font=("Segoe UI", 11, "bold"),
                text_color="#949ba4",
            ).pack(side="left")

            lbl_qtd = ctk.CTkLabel(
                header_card,
                text=" 0 ",
                font=("Segoe UI", 10, "bold"),
                fg_color=card["bg_subtil"],
                text_color=card["cor"],
                corner_radius=4,
            )
            lbl_qtd.pack(side="right")

            lbl_val = ctk.CTkLabel(
                conteudo,
                text="R$ 0,00",
                font=("Segoe UI", 22, "bold"),
                text_color="#ffffff",
            )
            lbl_val.pack(anchor="w", pady=(8, 0))

            dict_cards_ui[status_id] = {"qtd": lbl_qtd, "valor": lbl_val}

        # =========================================================================
        # 2. BARRA DE FILTROS E AÇÕES
        # =========================================================================
        frame_filtros = ctk.CTkFrame(parent, fg_color="transparent")
        frame_filtros.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        subframe_esquerda = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        subframe_esquerda.pack(side="left", fill="x")

        col_status = ctk.CTkFrame(subframe_esquerda, fg_color="transparent")
        col_status.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(col_status, text="Status:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(anchor="w")
        combo_status = ctk.CTkComboBox(
            col_status,
            values=["Todos", "Pendente", "Aprovado", "Cancelado"],
            width=140,
        )
        combo_status.pack(anchor="w")

        col_data_inicio = ctk.CTkFrame(subframe_esquerda, fg_color="transparent")
        col_data_inicio.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(col_data_inicio, text="Data Inicial:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(anchor="w")
        entry_data_inicio = ctk.CTkEntry(col_data_inicio, placeholder_text="DD/MM/AAAA", width=110, fg_color="#2b2b2b")
        entry_data_inicio.pack(anchor="w")

        col_data_fim = ctk.CTkFrame(subframe_esquerda, fg_color="transparent")
        col_data_fim.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(col_data_fim, text="Data Final:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(anchor="w")
        entry_data_fim = ctk.CTkEntry(col_data_fim, placeholder_text="DD/MM/AAAA", width=110, fg_color="#2b2b2b")
        entry_data_fim.pack(anchor="w")

        btn_filtrar = ctk.CTkButton(
            subframe_esquerda,
            text="Filtrar",
            width=90,
            command=lambda: on_filtrar_click(),
        )
        btn_filtrar.pack(side="left", padx=(5, 0), pady=(20, 0))

        # Botões Direita
        subframe_direita = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        subframe_direita.pack(side="right", fill="x")

        btn_exportar_excel = ctk.CTkButton(
            subframe_direita,
            text="Exportar Excel",
            fg_color="#2FA572",
            hover_color="#207B53",
            width=120,
            command=exportar_em_excel,
        )
        btn_exportar_excel.pack(side="right", padx=(5, 0), pady=(20, 0))

        btn_exportar_pdf = ctk.CTkButton(
            subframe_direita,
            text="Gerar PDF",
            fg_color="#2FA572",
            hover_color="#207B53",
            width=100,
            command=exportar_em_pdf,
        )
        btn_exportar_pdf.pack(side="right", padx=5, pady=(20, 0))

        # Preenchimento Padrão de Datas
        hoje = datetime.now()
        primeiro_dia_str = hoje.replace(day=1).strftime("%d/%m/%Y")
        _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
        dt_fim_str = hoje.replace(day=ultimo_dia).strftime("%d/%m/%Y")

        entry_data_inicio.insert(0, primeiro_dia_str)
        entry_data_fim.insert(0, dt_fim_str)

        # =========================================================================
        # 3. TABELA DE LISTAGEM DE ORÇAMENTOS
        # =========================================================================
        frame_tabela = ctk.CTkScrollableFrame(parent, fg_color="#141517", corner_radius=10)
        frame_tabela.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")

        headers = ["ID", "Consulta ID", "Paciente", "Valor", "Data", "Status", "Ações"]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(frame_tabela, text=text, font=("Segoe UI", 11, "bold"), text_color="#8d9c93")
            lbl.grid(row=0, column=col, padx=12, pady=10, sticky="w")

        # =========================================================================
        # FUNÇÕES DE LÓGICA E ATUALIZAÇÃO
        # =========================================================================
        def Helper_get_attr(item, atributo):
            """Lida dinamicamente se o retorno do SQL for Dict ou Objeto/Row."""
            if isinstance(item, dict):
                return item.get(atributo)
            return getattr(item, atributo, None)

        def atualizar_cards_resumo(lista_orcamentos):
            totais = {
                0: {"qtd": 0, "valor": 0.0},
                1: {"qtd": 0, "valor": 0.0},
                2: {"qtd": 0, "valor": 0.0},
            }

            for item in lista_orcamentos:
                #funciona tantto com dicionario quanto com object
                st = Helper_get_attr(item, "status")
                vl = float(Helper_get_attr(item, "valor") or 0)
                if st in totais:
                    totais[st]["qtd"] += 1
                    totais[st]["valor"] += vl


            # nao faco ideia do que acontece aqui
            for st_id, data in totais.items():
                if st_id in dict_cards_ui:
                    val_fmt = f"R$ {data['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    dict_cards_ui[st_id]["qtd"].configure(text=f" {data['qtd']} ")
                    dict_cards_ui[st_id]["valor"].configure(text=val_fmt)

        def renderizar_tabela(lista_orcamentos):
            for widget in frame_tabela.winfo_children():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()

            for index, o in enumerate(lista_orcamentos, start=1):
                o_id = Helper_get_attr(o, "id")
                consulta_id = Helper_get_attr(o, "consulta_id")
                paciente_nome = Helper_get_attr(o, "paciente_nome")
                valor = float(Helper_get_attr(o, "valor") or 0)
                data_criacao = Helper_get_attr(o, "data_criacao")
                status = Helper_get_attr(o, "status")

                # Grid das Colunas
                ctk.CTkLabel(frame_tabela, text=str(o_id), font=("Segoe UI", 12), text_color="#cfd0d4").grid(row=index, column=0, padx=12, pady=6, sticky="w")
                ctk.CTkLabel(frame_tabela, text=str(consulta_id), font=("Segoe UI", 12), text_color="#cfd0d4").grid(row=index, column=1, padx=12, pady=6, sticky="w")
                ctk.CTkLabel(frame_tabela, text=str(paciente_nome), font=("Segoe UI", 12), text_color="#cfd0d4").grid(row=index, column=2, padx=12, pady=6, sticky="w")

                val_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                ctk.CTkLabel(frame_tabela, text=val_str, font=("Segoe UI", 12), text_color="#cfd0d4").grid(row=index, column=3, padx=12, pady=6, sticky="w")

                dt_fmt = data_criacao.strftime("%d/%m/%Y %H:%M") if hasattr(data_criacao, "strftime") else str(data_criacao)[:16]
                ctk.CTkLabel(frame_tabela, text=dt_fmt, font=("Segoe UI", 12), text_color="#cfd0d4").grid(row=index, column=4, padx=12, pady=6, sticky="w")

                status_map = {0: "Pendente", 1: "Aprovado", 2: "Cancelado"}
                ctk.CTkLabel(frame_tabela, text=status_map.get(status, str(status)), font=("Segoe UI", 12, "bold"), text_color="#cfd0d4").grid(row=index, column=5, padx=12, pady=6, sticky="w")

                # Botões de Ação na Tabela (Corrigidos para aceitar id direto)
                frame_acoes = ctk.CTkFrame(frame_tabela, fg_color="transparent")
                frame_acoes.grid(row=index, column=6, padx=12, pady=8, sticky="w")

                btn_aprovar = ctk.CTkButton(
                    frame_acoes,
                    text="✓",
                    width=30,
                    height=24,
                    fg_color="#12331f",
                    hover_color="#1e4d31",
                    text_color="#4ade80",
                    command=lambda item_id=o_id: on_aprovar_click(item_id),
                )
                btn_aprovar.pack(side="left", padx=2)

                btn_cancelar = ctk.CTkButton(
                    frame_acoes,
                    text="✕",
                    width=30,
                    height=24,
                    fg_color="#381919",
                    hover_color="#592929",
                    text_color="#f87171",
                    command=lambda item_id=o_id: on_cancelar_click(item_id),
                )
                btn_cancelar.pack(side="left", padx=2)

        def on_filtrar_click():
            mapa_status = {"Todos": None, "Pendente": 0, "Aprovado": 1, "Cancelado": 2}
            status_id = mapa_status.get(combo_status.get(), None)

            dt_inicio_str = entry_data_inicio.get().strip()
            dt_fim_str = entry_data_fim.get().strip()

            dt_inicio, dt_fim = None, None
            try:
                if dt_inicio_str:
                    dt_inicio = datetime.strptime(dt_inicio_str, "%d/%m/%Y")
                if dt_fim_str:
                    dt_fim = datetime.strptime(dt_fim_str, "%d/%m/%Y")
            except ValueError:
                print("Formato de data inválido. Use DD/MM/AAAA")
                return

            orcamentos = lista_orcamentos_por_status_data(status_id, dt_inicio, dt_fim)
            renderizar_tabela(orcamentos)
            atualizar_cards_resumo(orcamentos)

        # Carga inicial ao abrir a tela
        on_filtrar_click()

    atualizar_orcamento()