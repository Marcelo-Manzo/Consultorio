import customtkinter as ctk
from datetime import datetime, timedelta

controle_mensal = {"deslocamento": 0}

def mostrar(parent):
    # Limpa a janela/container atual antes de renderizar
    for widget in parent.winfo_children():
        widget.destroy()

    def on_filtrar_click():
            """Sua tarefa: Ler `combo_status.get()` e buscar no banco filtrando por esse status."""
            pass
    
    def abrir_modal_novo_orcamento():
        """Sua tarefa: Abrir um ctk.CTkToplevel para entrada de dados de novo orçamento."""
        pass

    def on_aprovar_click(orcamento_id):
        """Sua tarefa: Dar UPDATE status = 1 no SQL Server para o orcamento_id."""
        pass

    def on_cancelar_click(orcamento_id):
        """Sua tarefa: Dar UPDATE status = 2 no SQL Server para o orcamento_id."""
        pass

    def atualizar_orcamento():

        # Layout Principal do Container
        parent.grid_rowconfigure(0, weight=0)  # Cards
        parent.grid_rowconfigure(1, weight=0)  # Filtros e Ações
        parent.grid_rowconfigure(2, weight=1)  # Tabela
        parent.grid_columnconfigure(0, weight=1)

        # =========================================================================
        # 1. CARDS DE RESUMO FINANCEIRO
        # =========================================================================
        frame_cards = ctk.CTkFrame(parent, fg_color="transparent")
        frame_cards.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        frame_cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        # Card Pendentes (Status 0)
        card_pendente = ctk.CTkFrame(frame_cards, border_width=2, border_color="#E6A100")
        card_pendente.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(card_pendente, text="PENDENTES (0)", font=("Arial", 12, "bold"), text_color="#E6A100").pack(pady=(10, 2))
        lbl_total_pendente = ctk.CTkLabel(card_pendente, text="R$ 0,00", font=("Arial", 18, "bold"))
        lbl_total_pendente.pack(pady=(0, 10))

        # Card Aprovados (Status 1)
        card_aprovado = ctk.CTkFrame(frame_cards, border_width=2, border_color="#2FA572")
        card_aprovado.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(card_aprovado, text="APROVADOS (1)", font=("Arial", 12, "bold"), text_color="#2FA572").pack(pady=(10, 2))
        lbl_total_aprovado = ctk.CTkLabel(card_aprovado, text="R$ 0,00", font=("Arial", 18, "bold"))
        lbl_total_aprovado.pack(pady=(0, 10))

        # Card Cancelados (Status 2)
        card_cancelado = ctk.CTkFrame(frame_cards, border_width=2, border_color="#EA4335")
        card_cancelado.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(card_cancelado, text="CANCELADOS (2)", font=("Arial", 12, "bold"), text_color="#EA4335").pack(pady=(10, 2))
        lbl_total_cancelado = ctk.CTkLabel(card_cancelado, text="R$ 0,00", font=("Arial", 18, "bold"))
        lbl_total_cancelado.pack(pady=(0, 10))

        # =========================================================================
        # 2. BARRA DE FILTROS E AÇÕES
        # =========================================================================
        frame_filtros = ctk.CTkFrame(parent, fg_color="transparent")
        frame_filtros.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Filtro de Status
        combo_status = ctk.CTkComboBox(
            frame_filtros, 
            values=["Todos", "0 - Pendente", "1 - Aprovado", "2 - Cancelado"]
        )
        combo_status.pack(side="left", padx=(0, 10))

        # Botão Filtrar
        btn_filtrar = ctk.CTkButton(
            frame_filtros, 
            text="Filtrar", 
            width=100, 
            command=lambda: on_filtrar_click()
        )
        btn_filtrar.pack(side="left", padx=5)

        # Botão Novo Orçamento
        btn_novo = ctk.CTkButton(
            frame_filtros, 
            text="+ Novo Orçamento", 
            fg_color="#2FA572", 
            hover_color="#207B53",
            command=lambda: abrir_modal_novo_orcamento()
        )
        btn_novo.pack(side="right")

        # =========================================================================
        # 3. TABELA DE LISTAGEM DE ORÇAMENTOS
        # =========================================================================
        frame_tabela = ctk.CTkScrollableFrame(parent)
        frame_tabela.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")

        # Cabeçalho da Tabela
        headers = ["ID", "Consulta ID", "Paciente", "Valor", "Data", "Status", "Ações"]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(frame_tabela, text=text, font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=col, padx=10, pady=10, sticky="w")

        # =========================================================================
        # FUNÇÕES INTERNAS E EVENTOS (Sua lógica entra aqui)
        # =========================================================================
        def atualizar_cards(pendente_val, aprovado_val, cancelado_val):
            """Sua tarefa: passar os valores do SQL Server para os labels."""
            lbl_total_pendente.configure(text=f"R$ {pendente_val:.2f}")
            lbl_total_aprovado.configure(text=f"R$ {aprovado_val:.2f}")
            lbl_total_cancelado.configure(text=f"R$ {cancelado_val:.2f}")

        def renderizar_tabela(lista_orcamentos):
            """
            Sua tarefa: Receber a lista do SQL Server e iterar renderizando as linhas.
            Status: 0 -> Pendente, 1 -> Aprovado, 2 -> Cancelado
            """
            # Limpa as linhas antigas (preservando o cabeçalho)
            for widget in frame_tabela.winfo_children():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()

            # Iteração de exemplo para preencher com seus dados do banco
            for index, item in enumerate(lista_orcamentos, start=1):
                ctk.CTkLabel(frame_tabela, text=str(item['id'])).grid(row=index, column=0, padx=10, pady=5)
                ctk.CTkLabel(frame_tabela, text=str(item['consulta_id'])).grid(row=index, column=1, padx=10, pady=5)
                ctk.CTkLabel(frame_tabela, text=item['paciente_nome']).grid(row=index, column=2, padx=10, pady=5)
                ctk.CTkLabel(frame_tabela, text=f"R$ {item['valor']:.2f}").grid(row=index, column=3, padx=10, pady=5)
                ctk.CTkLabel(frame_tabela, text=str(item['data_criacao'])).grid(row=index, column=4, padx=10, pady=5)

                # Mapeamento do Status Inteiro para Texto
                status_map = {0: "Pendente", 1: "Aprovado", 2: "Cancelado"}
                status_text = status_map.get(item['status'], "Desconhecido")
                ctk.CTkLabel(frame_tabela, text=status_text).grid(row=index, column=5, padx=10, pady=5)

                # Botões de Ação
                frame_acoes = ctk.CTkFrame(frame_tabela, fg_color="transparent")
                frame_acoes.grid(row=index, column=6, padx=10, pady=5)

                btn_aprovar = ctk.CTkButton(
                    frame_acoes, text="Aprovar", width=60, fg_color="#2FA572",
                    command=lambda id=item['id']: on_aprovar_click(id)
                )
                btn_aprovar.pack(side="left", padx=2)

                btn_cancelar = ctk.CTkButton(
                    frame_acoes, text="Cancelar", width=60, fg_color="#EA4335",
                    command=lambda id=item['id']: on_cancelar_click(id)
                )
                btn_cancelar.pack(side="left", padx=2)

    atualizar_orcamento()