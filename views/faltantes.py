import customtkinter as ctk
from datetime import datetime, timedelta
from database.models import listar_faltas_data,marcar_comparecimento,buscar_consulta_por_id_dict, criar_consulta

# 0 semanal, 1 mensal.
controle_semana = {"deslocamento": 0}

def mostrar(parent):

    def acao_remarcar(id_consulta):
        frame_editar_consulta = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        frame_editar_consulta.title("Remarcar Consulta")
        
        largura_janela = 400
        altura_janela = 220 # CORRIGIDO: Janela menor já que tem menos campos

        largura_tela = frame_editar_consulta.winfo_screenwidth()
        altura_tela = frame_editar_consulta.winfo_screenheight()

        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        frame_editar_consulta.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        frame_editar_consulta.grab_set()

        #====================CustomTkinter======================
        consulta = buscar_consulta_por_id_dict(id_consulta)

        lbl_topo = ctk.CTkLabel(frame_editar_consulta, text="Escolha a Nova Data e Horário", font=("Segoe UI", 15, "bold"), text_color="#ffffff")
        lbl_topo.pack(pady=15)

        data_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Data (DD/MM/AAAA)", fg_color="#2b2b2b")
        data_entry.pack(pady=6)
        # CORRIGIDO: Acesso por chave ["data"]
        data_entry.insert(0, consulta["data"].strftime('%d/%m/%Y')) 

        horario_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Horário", fg_color="#2b2b2b")
        horario_entry.pack(pady=6)
        # CORRIGIDO: Acesso por chave ["data"]
        horario_entry.insert(0, consulta["data"].strftime('%H:%M'))

        resultado_editar_label = ctk.CTkLabel(frame_editar_consulta, text="", font=("Segoe UI", 12))
        resultado_editar_label.pack(pady=5)

        def realizar_update():
            data_str = data_entry.get()
            horario_str = horario_entry.get()

            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                horario_obj = datetime.strptime(horario_str, "%H:%M").time()
                data_e_horario_final = datetime.combine(data_obj.date(), horario_obj)
            except ValueError:
                resultado_editar_label.configure(text="❌ Data ou Horário inválidos.", text_color="#ff4a4a")
                return

            # 1. Cria a consulta nova apontando para o PACIENTE correto
            criar_consulta(consulta["paciente_id"], consulta["tratamento"], data_e_horario_final, consulta["valor"], consulta["metodo_pagamento"])
            
            # 2. Atualiza a consulta antiga para o status 3 (Falta Remarcada)
            marcar_comparecimento(consulta["id"], status=3)
            
            # 3. Fecha a janela de edição/remarcação
            frame_editar_consulta.destroy()

            # 4. CRIA O POPUP DE SUCESSO PERSONALIZADO
            popup_sucesso = ctk.CTkToplevel(parent, fg_color="#1e1f22")
            popup_sucesso.title("Sucesso")
            popup_sucesso.geometry("300x150")
            
            # Centraliza o popup de sucesso na tela
            p_largura = 300
            p_altura = 150
            l_tela = popup_sucesso.winfo_screenwidth()
            a_tela = popup_sucesso.winfo_screenheight()
            pos_x = int((l_tela / 2) - (p_largura / 2))
            pos_y = int((a_tela / 2) - (p_altura / 2))
            popup_sucesso.geometry(f"{p_largura}x{p_altura}+{pos_x}+{pos_y}")
            
            popup_sucesso.grab_set() # Foca a atenção total no popup
            
            # Conteúdo do Popup
            lbl_msg = ctk.CTkLabel(popup_sucesso, text="✨ Consulta remarcada\ncom sucesso!", font=("Segoe UI", 14, "bold"), text_color="#ffffff")
            lbl_msg.pack(pady=(25, 15))
            
            def fechar_popup():
                popup_sucesso.destroy()
                # Só atualiza a tela de faltantes DEPOIS que ela clicar em OK
                atualizar_tabela_faltantes()

            btn_ok = ctk.CTkButton(popup_sucesso, text="OK", command=fechar_popup, fg_color="#1f6aa5", hover_color="#144870", width=100, font=("Segoe UI", 12, "bold"))
            btn_ok.pack()

        ctk.CTkButton(frame_editar_consulta, text="Salvar Alterações", command=realizar_update, fg_color="#1f6aa5", hover_color="#144870", font=("Segoe UI", 13, "bold"), height=35, width=180).pack(pady=15)
        
        print(f"Janela de remarcação aberta para a consulta ID: {id_consulta}")
        # REMOVIDO: Linha com acao_resolver_falta("id") deletada para não causar bugs de execução precoce

    def acao_resolver_falta(id_consulta):
        """
        Quando o usuário clica no '✔', significa que o paciente apareceu 
        (ou a falta foi resolvida).
        """
        marcar_comparecimento(id_consulta,2) # Salva no banco
        atualizar_tabela_faltantes()       # Atualiza a tela da sua sogra na hora!

    def abrir_detalhes_paciente(id_paciente):
        """
        O que fazer aqui:
        1. Executada quando o usuário dá um Duplo Clique na linha ou no nome do paciente.
        2. Você pode abrir uma janela mostrando o prontuário, telefone ou histórico do paciente.
        """

        # [SEU CÓDIGO AQUI]
        print(f"Duplo clique: Abrindo prontuário do paciente ID: {id_paciente}")
        pass


    def avanca_semana():
        controle_semana["deslocamento"] += 1
        atualizar_tabela_faltantes()

    def retroceder_semana():
        controle_semana["deslocamento"] -= 1
        atualizar_tabela_faltantes()
    
    def abrir_janela_detalhes(id_consulta):
        print(f"Abrindo detalhes da consulta ID: {id_consulta}")

    # =========================================================================
    # 2. ESTRUTURA VISUAL (FRONT-END)
    # =========================================================================
    
    # Título da Tela
    titulo = ctk.CTkLabel(parent, text="Pacientes Faltantes", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 5), anchor="center", padx=25)

    # Frame para agrupar os botões horizontais acima do cabeçalho da tabela
    frame_botoes = ctk.CTkFrame(parent, fg_color="transparent")
    frame_botoes.pack(pady=10, anchor="center", padx=25)

    # Botões de navegação posicionados lado a lado usando side="left"
    ctk.CTkButton(frame_botoes, text="◀ Anterior", command=retroceder_semana, width=100, fg_color="#2b2b2b", hover_color="#3a3a3a").pack(side="left", padx=5)
    ctk.CTkButton(
        frame_botoes, 
        text="🏠 Hoje", 
        command=lambda: [controle_semana.update({"deslocamento": 0}), atualizar_tabela_faltantes()], 
        width=80,
        fg_color="#2b2b2b",
        hover_color="#3a3a3a"
    ).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Próxima ▶", command=avanca_semana, width=100, fg_color="#2b2b2b", hover_color="#3a3a3a").pack(side="left", padx=5)

    # Cabeçalho Fixo da Tabela (Agora posicionado logo abaixo dos botões)
    frame_header = ctk.CTkFrame(parent, fg_color="#1b1c1e", height=35, corner_radius=5)
    frame_header.pack(fill="x", padx=25, pady=(10, 0))
    frame_header.pack_propagate(False)
    
    frame_header.columnconfigure(0, weight=2) # Coluna Paciente
    frame_header.columnconfigure(1, weight=1) # Coluna Data/Hora
    frame_header.columnconfigure(2, weight=2) # Coluna Tratamento
    frame_header.columnconfigure(3, weight=1) # Coluna Ações
    
    ctk.CTkLabel(frame_header, text="Paciente", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=0, sticky="w", padx=15, pady=5)
    ctk.CTkLabel(frame_header, text="Horário", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=1, sticky="w", padx=5, pady=5)
    ctk.CTkLabel(frame_header, text="Tratamento", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    ctk.CTkLabel(frame_header, text="Ações", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=3, sticky="e", padx=25, pady=5)

    # Área de rolagem para as linhas
    tabela_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    tabela_scroll.pack(fill="both", expand=True, padx=20, pady=5)

    # =========================================================================
    # 3. RENDERIZAÇÃO DINÂMICA (O Front cria, mas chama as SUAS funções)
    # =========================================================================
    def atualizar_tabela_faltantes():
        hoje = datetime.now()
        # Encontra a segunda-feira da semana alvo usando o deslocamento
        inicio_semana = hoje - timedelta(days=hoje.weekday()) + timedelta(weeks=controle_semana["deslocamento"])

        # Limpa tudo antes de redesenhar
        for widget in tabela_scroll.winfo_children():
            widget.destroy()
            
        dias_nomes = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
        idx_geral = 0 # Controlador para alternar as cores das linhas de forma contínua

        # Varrer cada dia útil da semana selecionada
        for i, nome_dia in enumerate(dias_nomes):
            data_dia = inicio_semana + timedelta(days=i)
            data_banco = data_dia.strftime('%Y-%m-%d')
            
            # Busca as faltas correspondentes especificamente a esta data
            faltantes = listar_faltas_data(data_banco)
            
            # Se existirem faltas para este dia, desenhamos o divisor e os cards
            if faltantes:
                data_formatada = data_dia.strftime('%d/%m')
                
                # Divisor sutil e limpo indicando o dia corrente
                lbl_divisor = ctk.CTkLabel(
                    tabela_scroll, 
                    text=f"📅 {nome_dia.upper()} — {data_formatada}", 
                    font=("Segoe UI", 12, "bold"), 
                    text_color="#1f6aa5"
                )
                lbl_divisor.pack(anchor="w", padx=15, pady=(15, 5))
                
                # Renderiza cada paciente faltou nesse dia específico
                for faltante in faltantes:
                    cor_linha = "#212225" if idx_geral % 2 == 0 else "#1c1d20"
                    idx_geral += 1
                    
                    linha_frame = ctk.CTkFrame(tabela_scroll, fg_color=cor_linha, height=50, corner_radius=6, border_width=1, border_color="#242528")
                    linha_frame.pack(fill="x", pady=4, padx=5)
                    linha_frame.pack_propagate(False)
                    
                    linha_frame.columnconfigure(0, weight=2)
                    linha_frame.columnconfigure(1, weight=1)
                    linha_frame.columnconfigure(2, weight=2)
                    linha_frame.columnconfigure(3, weight=1)
                    
                    # Coluna 0: Nome
                    lbl_nome = ctk.CTkLabel(linha_frame, text=faltante["nome"], font=("Segoe UI", 13, "bold"), text_color="#ffffff")
                    lbl_nome.grid(row=0, column=0, sticky="w", padx=10, pady=10)
                    
                    # Coluna 1: Tratando exibição apenas do Horário (Já que a data está no Divisor)
                    try:
                        if isinstance(faltante["data"], str):
                            # Tenta ler o formato padrão que vem do banco
                            data_obj = datetime.strptime(faltante["data"], "%Y-%m-%d %H:%M:%S")
                            horario_texto = data_obj.strftime("%H:%M")
                        else:
                            horario_texto = faltante["data"].strftime("%H:%M")
                    except Exception:
                        horario_texto = str(faltante["data"]) # Fallback de segurança

                    lbl_data = ctk.CTkLabel(linha_frame, text=horario_texto, font=("Segoe UI", 12), text_color="#cfd0d4")
                    lbl_data.grid(row=0, column=1, sticky="w", padx=5, pady=10)
                    
                    # Coluna 2: Tratamento
                    lbl_trat = ctk.CTkLabel(linha_frame, text=faltante["tratamento"], font=("Segoe UI", 12), text_color="#a0a0a5")
                    lbl_trat.grid(row=0, column=2, sticky="w", padx=5, pady=10)
                    
                    # Vinculando o Duplo Clique
                    linha_frame.bind("<Double-Button-1>", lambda event, p_id=faltante["id_paciente"]: abrir_detalhes_paciente(p_id))
                    lbl_nome.bind("<Double-Button-1>", lambda event, p_id=faltante["id_paciente"]: abrir_detalhes_paciente(p_id))
                    
                    # Coluna 3: Container dos Botões
                    frame_acoes = ctk.CTkFrame(linha_frame, fg_color="transparent")
                    frame_acoes.grid(row=0, column=3, sticky="e", padx=10, pady=5)
                    
                    # BOTÃO 1: Remarcar
                    ctk.CTkButton(
                        frame_acoes, 
                        text="Remarcar", 
                        command=lambda c_id=faltante["id_consulta"]: acao_remarcar(c_id),
                        width=75, height=26, font=("Segoe UI", 11, "bold"), corner_radius=5,
                        fg_color="#053d1c", hover_color="#04270d", text_color="#cfd0d4"
                    ).pack(side="left", padx=3)
                    
                    # BOTÃO 2: Resolver (✔)
                    ctk.CTkButton(
                        frame_acoes, 
                        text="✔", 
                        command=lambda c_id=faltante["id_consulta"]: acao_resolver_falta(c_id),
                        width=26, height=26, font=("Segoe UI", 11, "bold"), corner_radius=5,
                        fg_color="#2b2b2b", hover_color="#3a3a3a", text_color="#a0a0a5"
                    ).pack(side="left", padx=3)
            else: 
                data_formatada = data_dia.strftime('%d/%m')
                
                # Divisor sutil e limpo indicando o dia corrente
                lbl_divisor = ctk.CTkLabel(
                    tabela_scroll, 
                    text=f"📅 {nome_dia.upper()} — {data_formatada}", 
                    font=("Segoe UI", 12, "bold"), 
                    text_color="#1f6aa5"
                )
                lbl_divisor.pack(anchor="w", padx=15, pady=(15, 5))

                linha_frame = ctk.CTkFrame(tabela_scroll, height=50, corner_radius=6, border_width=1, border_color="#242528")
                linha_frame.pack(fill="x", pady=4, padx=5)
                linha_frame.pack_propagate(False)

                Linha_Compareceu = ctk.CTkLabel(linha_frame, text="Ninguém faltou nesse dia", font=("Segoe UI", 14, "bold"), text_color="#a0a0a5")
                # Faltou essa linha aqui embaixo:
                Linha_Compareceu.pack(side="left", padx=15, pady=10)

    # Primeira execução para desenhar a tabela na abertura
    atualizar_tabela_faltantes()