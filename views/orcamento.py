import customtkinter as ctk
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar
from database.models import lista_orcamentos_por_status_data

controle_mensal = {"deslocamento": 0}

def mostrar(parent):
    # Limpa a janela/container atual antes de renderizar
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
        pass

    def on_cancelar_click(orcamento_id):
        """Atualiza o status do orçamento para Cancelado (2) no banco de dados."""
        pass


    def atualizar_orcamento():
        # Layout Principal do Container
        parent.grid_rowconfigure(0, weight=0)  # Cards
        parent.grid_rowconfigure(1, weight=0)  # Filtros e Ações
        parent.grid_rowconfigure(2, weight=1)  # Tabela
        parent.grid_columnconfigure(0, weight=1)

        # =========================================================================
        # 1. CARDS DE RESUMO FINANCEIRO (ESTILO CLEAN)
        # =========================================================================
        frame_cards = ctk.CTkFrame(parent, fg_color="transparent")
        frame_cards.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        frame_cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        dados_cards = [
            {"titulo": "PENDENTES", "qtd": "0", "valor": "R$ 0,00", "cor": "#E6A100", "bg_subtil": "#2a2415"},
            {"titulo": "APROVADOS", "qtd": "0", "valor": "R$ 0,00", "cor": "#2FA572", "bg_subtil": "#162820"},
            {"titulo": "CANCELADOS", "qtd": "0", "valor": "R$ 0,00", "cor": "#EA4335", "bg_subtil": "#2b1919"},
        ]

        labels_valores_cards = []

        for col, card in enumerate(dados_cards):
            fundo_card = ctk.CTkFrame(
                frame_cards, 
                fg_color="#1e1f22", 
                border_width=1, 
                border_color="#2b2d31", 
                corner_radius=10
            )
            fundo_card.grid(row=0, column=col, padx=6, pady=5, sticky="ew")

            # Barra superior colorida sutil
            ctk.CTkFrame(fundo_card, fg_color=card["cor"], height=3, corner_radius=0).pack(fill="x", side="top")

            conteudo = ctk.CTkFrame(fundo_card, fg_color="transparent")
            conteudo.pack(fill="both", expand=True, padx=15, pady=12)

            header_card = ctk.CTkFrame(conteudo, fg_color="transparent")
            header_card.pack(fill="x")

            ctk.CTkLabel(
                header_card, 
                text=card["titulo"], 
                font=("Segoe UI", 11, "bold"), 
                text_color="#949ba4"
            ).pack(side="left")

            ctk.CTkLabel(
                header_card, 
                text=f" {card['qtd']} ", 
                font=("Segoe UI", 10, "bold"), 
                fg_color=card["bg_subtil"], 
                text_color=card["cor"],
                corner_radius=4
            ).pack(side="right")

            lbl_val = ctk.CTkLabel(
                conteudo, 
                text=card["valor"], 
                font=("Segoe UI", 22, "bold"), 
                text_color="#ffffff"
            )
            lbl_val.pack(anchor="w", pady=(8, 0))
            labels_valores_cards.append(lbl_val)

        # =========================================================================
        # 2. BARRA DE FILTROS E AÇÕES (ORGANIZADA)
        # =========================================================================

        frame_filtros = ctk.CTkFrame(parent, fg_color="transparent")
        frame_filtros.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Esquerda: Filtros de Status e Datas
        subframe_esquerda = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        subframe_esquerda.pack(side="left", fill="x")

        col_status = ctk.CTkFrame(subframe_esquerda, fg_color="transparent")
        col_status.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(col_status, text="Status:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(anchor="w")
        combo_status = ctk.CTkComboBox(
            col_status, 
            values=["Todos", "Pendente", "Aprovado", "Cancelado"],
            width=140
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
            command=lambda: on_filtrar_click()
        )
        btn_filtrar.pack(side="left", padx=(5, 0), pady=(20, 0))

        # Direita: Botões de Exportação
        subframe_direita = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        subframe_direita.pack(side="right", fill="x")

        btn_exportar_excel = ctk.CTkButton(
            subframe_direita, 
            text="Exportar Excel", 
            fg_color="#2FA572", 
            hover_color="#207B53",
            width=120,
            command=lambda: exportar_em_excel()
        )
        btn_exportar_excel.pack(side="right", padx=(5, 0), pady=(20, 0))

        btn_exportar_pdf = ctk.CTkButton(
            subframe_direita, 
            text="Gerar PDF", 
            fg_color="#2FA572", 
            hover_color="#207B53",
            width=100,
            command=lambda: exportar_em_pdf()
        )
        btn_exportar_pdf.pack(side="right", padx=5, pady=(20, 0))

        #================================
        # PREENCHENDO A DATA INICIAl DO MES

        hoje = datetime.now()
        # Gera a string "01/MM/AAAA" do mês atual
        primeiro_dia_str = datetime.now().replace(day=1).strftime("%d/%m/%Y")

        # Insere por padrão no input de data inicial da sua tela
        entry_data_inicio.delete(0, "end")
        entry_data_inicio.insert(0, primeiro_dia_str)

        #===============================
        # PREENCHENDO A DATA FINAL DO MES

        # Primeiro dia: 01/MM/AAAA
        dt_fim_str = hoje.replace(day=1).strftime("%d/%m/%Y")

        # Último dia: DD/MM/AAAA
        _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
        dt_fim_str = hoje.replace(day=ultimo_dia).strftime("%d/%m/%Y")

        # Insere nos inputs da tela

        entry_data_fim.delete(0, "end")
        entry_data_fim.insert(0, dt_fim_str)

        # =========================================================================
        # LÓGICA DE FILTRAGEM
        # =========================================================================
        def on_filtrar_click():
            for widget in frame_tabela.winfo_children():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()
            mapa_status = {
                "Todos": None,
                "Pendente": 0,
                "Aprovado": 1,
                "Cancelado": 2
            }
            
            texto_selecionado = combo_status.get()
            # Pega o valor correspondente (se não achar, assume None)
            status_id = mapa_status.get(texto_selecionado, None)
            
            # Agora status_id será 0, 1, 2 ou None
            print(f"Status para o SQL: {status_id}")

            print(f"status = {status_id}")

            dt_inicio_str = entry_data_inicio.get().strip()
            dt_fim_str = entry_data_fim.get().strip()

            dt_inicio = None
            dt_fim = None

            try:
                if dt_inicio_str:
                    dt_inicio = datetime.strptime(dt_inicio_str, "%d/%m/%Y")
                if dt_fim_str:
                    dt_fim = datetime.strptime(dt_fim_str, "%d/%m/%Y")
            except ValueError:
                print("Formato de data inválido. Use DD/MM/AAAA")
                return

            orcamentos = lista_orcamentos_por_status_data(status_id, dt_inicio, dt_fim)
            for index, o in enumerate(orcamentos, start=1):
    
                # Coluna 0 - ID
                ctk.CTkLabel(
                    frame_tabela, text=str(o.id), font=("Segoe UI", 12), text_color="#cfd0d4"
                ).grid(row=index, column=0, padx=12, pady=6, sticky="w")

                # Coluna 1 - Consulta ID
                ctk.CTkLabel(
                    frame_tabela, text=str(o.consulta_id), font=("Segoe UI", 12), text_color="#cfd0d4"
                ).grid(row=index, column=1, padx=12, pady=6, sticky="w")

                # Coluna 2 - Paciente (Nome ou ID)
                ctk.CTkLabel(
                    frame_tabela, text=str(o.paciente_nome), font=("Segoe UI", 12), text_color="#cfd0d4"
                ).grid(row=index, column=2, padx=12, pady=6, sticky="w")

                # Coluna 3 - Valor (formatado em R$)
                ctk.CTkLabel(
                    frame_tabela, text=f"R$ {float(o.valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                    font=("Segoe UI", 12), text_color="#cfd0d4"
                ).grid(row=index, column=3, padx=12, pady=6, sticky="w")

                # Coluna 4 - Data
                data_str = o.data_criacao.strftime("%d/%m/%Y %H:%M") if hasattr(o.data_criacao, "strftime") else str(o.data_criacao)[:16]
                ctk.CTkLabel(
                    frame_tabela, text=data_str, font=("Segoe UI", 12), text_color="#cfd0d4"
                ).grid(row=index, column=4, padx=12, pady=6, sticky="w")

                # Coluna 5 - Status (Texto em vez de número)
                status_map = {0: "Pendente", 1: "Aprovado", 2: "Cancelado"}
                status_texto = status_map.get(o.status, str(o.status))
                
                ctk.CTkLabel(
                    frame_tabela, text=status_texto, font=("Segoe UI", 12, "bold"), text_color="#cfd0d4"
                ).grid(row=index, column=5, padx=12, pady=6, sticky="w")
            

            print(f"Filtrando -> Status: {status_id} | De: {dt_inicio} | Até: {dt_fim}")

        # =========================================================================
        # 3. TABELA DE LISTAGEM DE ORÇAMENTOS
        # =========================================================================

        frame_tabela = ctk.CTkScrollableFrame(parent, fg_color="#141517", corner_radius=10)
        frame_tabela.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")

        # Cabeçalho da Tabela Clean
        headers = ["ID", "Consulta ID", "Paciente", "Valor", "Data", "Status", "Ações"]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(frame_tabela, text=text, font=("Segoe UI", 11, "bold"), text_color="#8d9c93")
            lbl.grid(row=0, column=col, padx=12, pady=10, sticky="w")


        # =========================================================================
        # FUNÇÕES INTERNAS E EVENTOS
        # =========================================================================
        def atualizar_cards(pendente_val, aprovado_val, cancelado_val):
            labels_valores_cards[0].configure(text=f"R$ {pendente_val:.2f}")
            labels_valores_cards[1].configure(text=f"R$ {aprovado_val:.2f}")
            labels_valores_cards[2].configure(text=f"R$ {cancelado_val:.2f}")

        def renderizar_tabela(lista_orcamentos):
            for widget in frame_tabela.winfo_children():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()

            for index, item in enumerate(lista_orcamentos, start=1):
                ctk.CTkLabel(frame_tabela, text=str(item['id']), font=("Segoe UI", 11)).grid(row=index, column=0, padx=12, pady=8, sticky="w")
                ctk.CTkLabel(frame_tabela, text=str(item['consulta_id']), font=("Segoe UI", 11)).grid(row=index, column=1, padx=12, pady=8, sticky="w")
                ctk.CTkLabel(frame_tabela, text=item['paciente_nome'], font=("Segoe UI", 11, "bold")).grid(row=index, column=2, padx=12, pady=8, sticky="w")
                ctk.CTkLabel(frame_tabela, text=f"R$ {item['valor']:.2f}", font=("Segoe UI", 11)).grid(row=index, column=3, padx=12, pady=8, sticky="w")
                ctk.CTkLabel(frame_tabela, text=str(item['data_criacao']), font=("Segoe UI", 11)).grid(row=index, column=4, padx=12, pady=8, sticky="w")

                # Badge de Status (Pílula)
                status_code = item['status']
                mapa_status = {
                    0: {"texto": "Pendente", "cor": "#E6A100", "bg": "#33270d"},
                    1: {"texto": "Aprovado", "cor": "#4ade80", "bg": "#12331f"},
                    2: {"texto": "Cancelado", "cor": "#f87171", "bg": "#381919"}
                }
                info_status = mapa_status.get(status_code, {"texto": "Desconhecido", "cor": "#888", "bg": "#222"})

                badge = ctk.CTkLabel(
                    frame_tabela,
                    text=f"  {info_status['texto']}  ",
                    font=("Segoe UI", 10, "bold"),
                    text_color=info_status["cor"],
                    fg_color=info_status["bg"],
                    corner_radius=10,
                    height=20
                )
                badge.grid(row=index, column=5, padx=12, pady=8, sticky="w")

                # Botões de Ação na Tabela
                frame_acoes = ctk.CTkFrame(frame_tabela, fg_color="transparent")
                frame_acoes.grid(row=index, column=6, padx=12, pady=8, sticky="w")

                btn_aprovar = ctk.CTkButton(
                    frame_acoes, text="✓", width=30, height=24, fg_color="#12331f", hover_color="#1e4d31", text_color="#4ade80",
                    command=lambda id=item['id']: on_aprovar_click(id)
                )
                btn_aprovar.pack(side="left", padx=2)

                btn_cancelar = ctk.CTkButton(
                    frame_acoes, text="✕", width=30, height=24, fg_color="#381919", hover_color="#592929", text_color="#f87171",
                    command=lambda id=item['id']: on_cancelar_click(id)
                )
                btn_cancelar.pack(side="left", padx=2)

    atualizar_orcamento()