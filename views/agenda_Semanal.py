import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_com_paciente_por_data, buscar_paciente_por_id, deletar_consulta, update_consulta, listar_tratamentos
from datetime import datetime, timedelta

# Variável de controle fora da função para reter o valor entre os redesenhos da tela
# 0 = Semana Atual | 1 = Próxima Semana | -1 = Semana Anterior
controle_semana = {"deslocamento": 0}

def mostrar(parent):
    # Dicionário para reter referências estáticas e atualizar os dados diretamente na memória
    componentes_agenda = {
        "lista_scrolls": [], 
        "labels_data": []
    }

    # Mantido estático no topo da função: Carrega uma única vez na memória
    horarios = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30','13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00']
    
    # Nova abordagem limpa: atualiza textos e substitui apenas os cards de consultas
    def atualizar_dados_agenda():
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday()) + timedelta(weeks=controle_semana["deslocamento"])

        mes_ano_texto = inicio_semana.strftime("%B / %Y").capitalize()
        titulo.configure(text=f"Agenda — {mes_ano_texto}")
        
        # Loop para varrer as colunas fixas e atualizar o conteúdo interno de cada dia
        for i in range(5):
            data_dia = inicio_semana + timedelta(days=i)
            
            # Atualiza dinamicamente o texto do cabeçalho da coluna (ex: "18/05")
            componentes_agenda["labels_data"][i].configure(text=data_dia.strftime('%d/%m'))
            
            # Limpa estritamente APENAS os cards antigos de dentro do frame de rolagem
            scroll_dia = componentes_agenda["lista_scrolls"][i]
            for widget in scroll_dia.winfo_children():
                widget.destroy()

            # Formata a data atual da coluna para o banco de dados
            data_banco = data_dia.strftime('%Y-%m-%d')
            
            # Busca todas as consultas do dia contendo o JOIN com os dados dos pacientes mapeados
            consultas_dia = listar_consultas_com_paciente_por_data(data_banco)
            
            # Varremos a lista estática de horários um por um
            for hora_teste in horarios:
                
                # Procura se existe alguma consulta no banco de dados para a hora corrente
                consulta_encontrada = None
                for c in consultas_dia:
                    if c["data"].strftime('%H:%M') == hora_teste:
                        consulta_encontrada = c
                        break
                
                if consulta_encontrada:
                    # ==================================================================
                    # CARD OCUPADO: Existe agendamento no horário
                    # ==================================================================
                    consulta_frame = ctk.CTkFrame(scroll_dia, fg_color="#212225", border_width=1, border_color="#3a3a3a", corner_radius=8)
                    consulta_frame.pack(fill="x", padx=2, pady=4)

                    # Configuração de colunas internas do Card
                    consulta_frame.columnconfigure(0, weight=1) # Bloco de textos (pega a esquerda toda)
                    consulta_frame.columnconfigure(1, weight=0) # Botão Editar compactado
                    consulta_frame.columnconfigure(2, weight=0) # Botão Excluir compacto

                    # 1. Sub-frame exclusivo para organizar os textos verticalmente sem afetar os botõeslaterais
                    sub_frame_texto = ctk.CTkFrame(consulta_frame, fg_color="transparent")
                    sub_frame_texto.grid(row=0, column=0, sticky="w", padx=8, pady=6)

                    # Linha 1: Horário destacado em azul/verde claro + Nome do Paciente reto
                    texto_topo = f"{hora_teste} - {consulta_encontrada['nome']}"
                    lbl_topo = ctk.CTkLabel(sub_frame_texto, text=texto_topo, justify="left", font=("Segoe UI", 11, "bold"), text_color="#8d9c93")
                    lbl_topo.pack(anchor="w")

                    # Linha 2: Tratamento logo abaixo, com uma cor mais sutil (cinza claro) para dar hierarquia visual
                    lbl_sub = ctk.CTkLabel(sub_frame_texto, text=consulta_encontrada['tratamento'], justify="left", font=("Segoe UI", 10), text_color="#94a8c9")
                    lbl_sub.pack(anchor="w")

                    # ID correto da consulta vindo do JOIN para amarrar as ações
                    c_id = consulta_encontrada["consulta_id"]

                    # Sistema de Duplo Clique aplicado no frame e nas duas labels de texto
                    consulta_frame.bind("<Double-Button-1>", lambda event, id_c=c_id: abrir_janela_detalhes(id_c))
                    lbl_topo.bind("<Double-Button-1>", lambda event, id_c=c_id: abrir_janela_detalhes(id_c))
                    lbl_sub.bind("<Double-Button-1>", lambda event, id_c=c_id: abrir_janela_detalhes(id_c))

                    # Botão "Editar" mantido alinhado na extrema direita
                    ctk.CTkButton(
                        consulta_frame, 
                        text="Editar", 
                        command=lambda c=consulta_encontrada: abrir_janela_editar(c), 
                        width=42,
                        height=24,
                        font=("Segoe UI", 10, "bold"),
                        corner_radius=5,
                        fg_color="#053d1c",
                        hover_color="#04270d",
                        text_color="#cfd0d4"
                    ).grid(row=0, column=1, sticky="e", padx=(0, 4), pady=8)

                    # Botão de excluir consulta mantido alinhado na extrema direita
                    ctk.CTkButton(
                        consulta_frame, 
                        text="❌", 
                        command=lambda id_c=c_id: [deletar_consulta(id_c), atualizar_dados_agenda()], 
                        width=24,
                        height=24,
                        corner_radius=5,
                        fg_color="#361a1a",
                        hover_color="#542323",
                        text_color="#f87171"
                    ).grid(row=0, column=2, sticky="e", padx=(0, 8), pady=8)
                
                else:
                    # ==================================================================
                    # CARD VAZIO: Horário livre para sua sogra agendar
                    # ==================================================================
                    btn_vazio = ctk.CTkButton(
                        scroll_dia,
                        text=f"➕  {hora_teste}",
                        font=("Segoe UI", 11, "bold"),
                        text_color="#888888",
                        fg_color="#1a1b1e",
                        hover_color="#232429",
                        border_width=1,
                        border_color="#2b2b2b",
                        corner_radius=6,
                        height=35,
                        # Passa a data da coluna e a hora do bloco para preencher o formulário futuro
                        command=lambda d=data_banco, h=hora_teste: abrir_janela_novo_agendamento(d, h)
                    )
                    btn_vazio.pack(fill="x", padx=4, pady=3)

    # Funções de navegação alterando o estado do deslocamento global de forma limpa
    def avanca_semana():
        controle_semana["deslocamento"] += 1
        atualizar_dados_agenda()

    def retroceder_semana():
        controle_semana["deslocamento"] -= 1
        atualizar_dados_agenda()
    
    def abrir_janela_detalhes(id_consulta):
        print(f"Abrindo detalhes da consulta ID: {id_consulta}")
        
    def abrir_janela_novo_agendamento(data_selecionada, horario_selecionado):
        print(f"Abrindo formulário de cadastro para o dia {data_selecionada} às {horario_selecionado}")
        # Próximo passo: Construir o formulário de inclusão aqui dentro!
    
    def abrir_janela_editar(consulta):
        frame_editar_consulta = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        frame_editar_consulta.title("Editar Consulta")
        
        largura_janela = 400
        altura_janela = 380

        largura_tela = frame_editar_consulta.winfo_screenwidth()
        altura_tela = frame_editar_consulta.winfo_screenheight()

        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        frame_editar_consulta.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        frame_editar_consulta.grab_set()

        #====================CustomTkinter======================
        lbl_topo = ctk.CTkLabel(frame_editar_consulta, text="Editar Agendamento", font=("Segoe UI", 16, "bold"), text_color="#ffffff")
        lbl_topo.pack(pady=15)

        tratamentos_db = listar_tratamentos()
        tratamentos_lista = [t.nome for t in tratamentos_db]
        
        tratamento_dropdown = ctk.CTkComboBox(frame_editar_consulta, values=tratamentos_lista, width=280, fg_color="#2b2b2b", button_color="#3a3a3a")
        tratamento_dropdown.pack(pady=6)
        # Adaptado para ler da chave do dicionário do JOIN ['tratamento']
        tratamento_dropdown.set(consulta['tratamento'])

        data_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Data (DD/MM/AAAA)", fg_color="#2b2b2b")
        data_entry.pack(pady=6)
        data_entry.insert(0, consulta['data'].strftime('%d/%m/%Y')) 

        horario_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Horário", fg_color="#2b2b2b")
        horario_entry.pack(pady=6)
        horario_entry.insert(0, consulta['data'].strftime('%H:%M'))

        valor_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Valor (ex: 150.00)", fg_color="#2b2b2b")
        valor_entry.pack(pady=6)
        valor_entry.insert(0, str(consulta['valor']))

        metodo_dropdown = ctk.CTkComboBox(frame_editar_consulta, values=["Pix", "Débito", "Crédito", "Dinheiro", "Pendente"], width=280, fg_color="#2b2b2b", button_color="#3a3a3a")
        metodo_dropdown.pack(pady=6)
        metodo_dropdown.set(consulta['metodo_pagamento'] if 'metodo_pagamento' in consulta else "Método de pagamento")

        resultado_editar_label = ctk.CTkLabel(frame_editar_consulta, text="", font=("Segoe UI", 12))
        resultado_editar_label.pack(pady=5)

        def realizar_update():
            novo_tratamento = tratamento_dropdown.get()
            data_str = data_entry.get()
            horario_str = horario_entry.get()
            novo_valor = valor_entry.get()
            novo_metodo = metodo_dropdown.get()

            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                horario_obj = datetime.strptime(horario_str, "%H:%M").time()
                data_e_horario_final = datetime.combine(data_obj.date(), horario_obj)
            except ValueError:
                resultado_editar_label.configure(text="❌ Data ou Horário inválidos.", text_color="#ff4a4a")
                return

            # Atualiza usando a chave de ID correta da consulta
            update_consulta(consulta['consulta_id'], novo_tratamento, data_e_horario_final, novo_valor, novo_metodo)
            frame_editar_consulta.destroy()

            # Atualiza os dados sem quebrar a renderização
            atualizar_dados_agenda()

        ctk.CTkButton(frame_editar_consulta, text="Salvar Alterações", command=realizar_update, fg_color="#1f6aa5", hover_color="#144870", font=("Segoe UI", 13, "bold"), height=35, width=180).pack(pady=15)

    # Título da tela (Instanciado fixo apenas UMA vez)
    titulo = ctk.CTkLabel(parent, font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 5))

    # Frame para agrupar os botões lado a lado no topo
    frame_botoes = ctk.CTkFrame(parent, fg_color="transparent")
    frame_botoes.pack(pady=10)

    ctk.CTkButton(frame_botoes, text="◀ Anterior", command=retroceder_semana, width=100, fg_color="#2b2b2b", hover_color="#3a3a3a").pack(side="left", padx=5)
    ctk.CTkButton(
        frame_botoes, 
        text="🏠 Hoje", 
        command=lambda: [controle_semana.update({"deslocamento": 0}), atualizar_dados_agenda()], 
        width=80,
        fg_color="#2b2b2b",
        hover_color="#3a3a3a"
    ).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Próxima ▶", command=avanca_semana, width=100, fg_color="#2b2b2b", hover_color="#3a3a3a").pack(side="left", padx=5)

    # Frame container estático do calendário semanal (Criado apenas UMA vez)
    frame_calendario = ctk.CTkFrame(parent, fg_color="transparent")
    frame_calendario.pack(fill="both", expand=True, padx=15, pady=10)
    frame_calendario.rowconfigure(0, weight=1)
    
    dias_nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # LAÇO INICIAL DE ESTRUTURA: Executado estaticamente uma única vez ao carregar a aba
    for i in range(5):
        frame_calendario.columnconfigure(i, weight=1, uniform="col")
        
        dia_container = ctk.CTkFrame(frame_calendario, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
        dia_container.grid(row=0, column=i, sticky="nsew", padx=4, pady=4)
        
        frame_cabecalho_dia = ctk.CTkFrame(dia_container, fg_color="#1b1c1e", height=50, corner_radius=8)
        frame_cabecalho_dia.pack(fill="x", padx=5, pady=5)
        frame_cabecalho_dia.pack_propagate(False)
        
        lbl_nome_dia = ctk.CTkLabel(frame_cabecalho_dia, text=dias_nomes[i], font=("Segoe UI", 13, "bold"), text_color="#a0a0a5")
        lbl_nome_dia.pack(pady=(5, 0))
        
        # Guardamos o ponteiro da label de data para atualizá-la futuramente sem quebras
        lbl_data_dia = ctk.CTkLabel(frame_cabecalho_dia, text="", font=("Segoe UI", 11), text_color="#68696e")
        lbl_data_dia.pack()
        componentes_agenda["labels_data"].append(lbl_data_dia)

        # O container rolável das consultas torna-se permanente; guardamos o ponteiro na lista
        lista_consultas = ctk.CTkScrollableFrame(dia_container, fg_color="transparent", label_text="")
        lista_consultas.pack(fill="both", expand=True, padx=4, pady=(0, 5))
        componentes_agenda["lista_scrolls"].append(lista_consultas)

    # Executa a primeira renderização dos dados assim que a visualização da agenda abre
    atualizar_dados_agenda()