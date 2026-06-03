import customtkinter as ctk
from datetime import datetime, timedelta
from database.models import 

#0 semanal, 1 mensal.
controle_periodo = {"periodo": 0}

def mostrar(parent):

    def acao_remarcar(id_consulta):
        """
        O que fazer aqui:
        1. Você recebe o ID da consulta que o paciente faltou.
        2. Pode abrir uma nova janela (ctk.CTkToplevel) com o formulário de agendamento.
        3. Dica: Você pode pré-preencher o nome do paciente nessa nova janela usando o id_consulta.
        """
        # [SEU CÓDIGO AQUI]
        print(f"Botão Remarcar clicado para a consulta ID: {id_consulta}")
        pass

    def acao_resolver_falta(id_consulta):
        """
        O que fazer aqui:
        1. Quando o usuário clica no '✔', significa que a falta foi tratada/justificada.
        2. Você deve ir no banco de dados e atualizar o status dessa consulta (ex: de 'Faltou' para 'Justificado' ou 'Arquivado').
        3. Após atualizar o banco, chame a função `atualizar_tabela_faltantes()` para a linha sumir da tela na hora!
        """
        # [SEU CÓDIGO AQUI]
        print(f"Botão Resolver (✔) clicado para a consulta ID: {id_consulta}")
        # atualizar_tabela_faltantes() # <-- Descomente isso quando fizer o código acima
        pass

    def abrir_detalhes_paciente(id_paciente):
        """
        O que fazer aqui:
        1. Executada quando o usuário dá um Duplo Clique na linha ou no nome do paciente.
        2. Você pode abrir uma janela mostrando o prontuário, telefone ou histórico do paciente.
        """
        # [SEU CÓDIGO AQUI]
        print(f"Duplo clique: Abrindo prontuário do paciente ID: {id_paciente}")
        pass


    # =========================================================================
    # 2. ESTRUTURA VISUAL (FRONT-END)
    # =========================================================================
    
    # Título da Tela
    titulo = ctk.CTkLabel(parent, text="Pacientes Faltantes", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 5), anchor="w", padx=25)
    
    subtitulo = ctk.CTkLabel(parent, text="Gerencie os agendamentos que não foram comparecidos", font=("Segoe UI", 13), text_color="#a0a0a5")
    subtitulo.pack(pady=(0, 15), anchor="w", padx=25)

    # Cabeçalho Fixo da Tabela
    frame_header = ctk.CTkFrame(parent, fg_color="#1b1c1e", height=35, corner_radius=5)
    frame_header.pack(fill="x", padx=25, pady=(10, 0))
    frame_header.pack_propagate(False)
    
    frame_header.columnconfigure(0, weight=2) # Coluna Paciente
    frame_header.columnconfigure(1, weight=1) # Coluna Data/Hora
    frame_header.columnconfigure(2, weight=2) # Coluna Tratamento
    frame_header.columnconfigure(3, weight=1) # Coluna Ações
    
    ctk.CTkLabel(frame_header, text="Paciente", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=0, sticky="w", padx=15, pady=5)
    ctk.CTkLabel(frame_header, text="Data / Hora", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=1, sticky="w", padx=5, pady=5)
    ctk.CTkLabel(frame_header, text="Tratamento", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    ctk.CTkLabel(frame_header, text="Ações", font=("Segoe UI", 12, "bold"), text_color="#a0a0a5").grid(row=0, column=3, sticky="e", padx=25, pady=5)

    # Área de rolagem para as linhas
    tabela_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    tabela_scroll.pack(fill="both", expand=True, padx=20, pady=5)

    # =========================================================================
    # 3. RENDERIZAÇÃO DINÂMICA (O Front cria, mas chama as SUAS funções)
    # =========================================================================
    def atualizar_tabela_faltantes():
        for widget in tabela_scroll.winfo_children():
            widget.destroy()
            
        # TODO: No futuro, substitua essa lista simulada por uma busca real no seu banco:
        # Ex: faltantes_db = buscar_faltantes_no_banco()
        faltantes_simulados = [
            {"id_consulta": 101, "id_paciente": 5, "nome": "Marcos Silva", "data": "28/05/2026 14:00", "tratamento": "Drenagem Linfática"},
            {"id_consulta": 102, "id_paciente": 12, "nome": "Ana Júlia Costa", "data": "01/06/2026 09:30", "tratamento": "Limpeza de Pele Premium"}
        ]
        
        for idx, faltante in enumerate(faltantes_simulados):
            cor_linha = "#141517" if idx % 2 == 0 else "#1c1d20"
            
            linha_frame = ctk.CTkFrame(tabela_scroll, fg_color=cor_linha, height=50, corner_radius=6, border_width=1, border_color="#242528")
            linha_frame.pack(fill="x", pady=4, padx=5)
            linha_frame.pack_propagate(False)
            
            linha_frame.columnconfigure(0, weight=2)
            linha_frame.columnconfigure(1, weight=1)
            linha_frame.columnconfigure(2, weight=2)
            linha_frame.columnconfigure(3, weight=1)
            
            # Textos das Colunas
            lbl_nome = ctk.CTkLabel(linha_frame, text=faltante["nome"], font=("Segoe UI", 13, "bold"), text_color="#ffffff")
            lbl_nome.grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            lbl_data = ctk.CTkLabel(linha_frame, text=faltante["data"], font=("Segoe UI", 12), text_color="#cfd0d4")
            lbl_data.grid(row=0, column=1, sticky="w", padx=5, pady=10)
            
            lbl_trat = ctk.CTkLabel(linha_frame, text=faltante["tratamento"], font=("Segoe UI", 12), text_color="#a0a0a5")
            lbl_trat.grid(row=0, column=2, sticky="w", padx=5, pady=10)
            
            # Vinculando o Duplo Clique (Passando o ID do paciente para a sua função)
            linha_frame.bind("<Double-Button-1>", lambda event, p_id=faltante["id_paciente"]: abrir_detalhes_paciente(p_id))
            lbl_nome.bind("<Double-Button-1>", lambda event, p_id=faltante["id_paciente"]: abrir_detalhes_paciente(p_id))
            
            # Container dos Botões
            frame_acoes = ctk.CTkFrame(linha_frame, fg_color="transparent")
            frame_acoes.grid(row=0, column=3, sticky="e", padx=10, pady=5)
            
            # BOTÃO 1: Remarcar -> Chama a sua função passando o ID da consulta
            ctk.CTkButton(
                frame_acoes, 
                text="Remarcar", 
                command=lambda c_id=faltante["id_consulta"]: acao_remarcar(c_id),
                width=75, height=26, font=("Segoe UI", 11, "bold"), corner_radius=5,
                fg_color="#053d1c", hover_color="#04270d", text_color="#cfd0d4"
            ).pack(side="left", padx=3)
            
            # BOTÃO 2: Resolver (✔) -> Chama a sua função passando o ID da consulta
            ctk.CTkButton(
                frame_acoes, 
                text="✔", 
                command=lambda c_id=faltante["id_consulta"]: acao_resolver_falta(c_id),
                width=26, height=26, font=("Segoe UI", 11, "bold"), corner_radius=5,
                fg_color="#2b2b2b", hover_color="#3a3a3a", text_color="#a0a0a5"
            ).pack(side="left", padx=3)

    # Primeira execução para desenhar a tabela na abertura
    atualizar_tabela_faltantes()