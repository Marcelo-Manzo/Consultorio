import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_paciente, listar_tratamentos, buscar_paciente_por_nome, listar_consultas_data
from datetime import datetime

def mostrar(parent):
    horarios_padrao = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]
    
    titulo = ctk.CTkLabel(parent, text="Agendamentos & Consultas", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 10))
    
    # CONTAINER CENTRAL: Divide a tela em duas colunas paralelas (Formulário na esquerda, Lista na direita)
    container_principal = ctk.CTkFrame(parent, fg_color="transparent")
    container_principal.pack(fill="both", expand=True, padx=20, pady=10)
    container_principal.columnconfigure(0, weight=1, uniform="coluna")
    container_principal.columnconfigure(1, weight=1, uniform="coluna")
    container_principal.rowconfigure(0, weight=1)

    # SUB-FRAME ESQUERDO: Guarda todos os campos de entrada de dados (Estilizado como bloco Premium)
    frame_formulario = ctk.CTkFrame(container_principal, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
    frame_formulario.grid(row=0, column=0, sticky="nsew", padx=15, pady=5)

    # SUB-FRAME DIREITO: Guarda o histórico de consultas do paciente selecionado
    frame_historico = ctk.CTkFrame(container_principal, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
    frame_historico.grid(row=0, column=1, sticky="nsew", padx=15, pady=5)

    # --- ELEMENTOS DO FORMULÁRIO (ESQUERDA) ---
    lbl_secao_form = ctk.CTkLabel(frame_formulario, text="Novo Agendamento", font=("Segoe UI", 16, "bold"), text_color="#ffffff")
    lbl_secao_form.pack(pady=(20, 15))

    # [GRUPO 1]: IDENTIFICAÇÃO DO PACIENTE (Organizado em linha com respiro calculado)
    frame_busca_linha = ctk.CTkFrame(frame_formulario, fg_color="transparent")
    frame_busca_linha.pack(pady=(5, 2), padx=30, fill="x")
    frame_busca_linha.columnconfigure(0, weight=1)
    frame_busca_linha.columnconfigure(1, weight=0)

    # Buscar paciente por nome (Movido para o frame_formulario)
    nome_busca_entry = ctk.CTkEntry(frame_busca_linha, placeholder_text="Nome do paciente", fg_color="#2b2b2b", height=35)
    nome_busca_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
    
    # resposta (Movido para o frame_formulario)
    resultado_label = ctk.CTkLabel(frame_formulario, text="", font=("Segoe UI", 12))
    resultado_label.pack(pady=(2, 10))

    # declaração do paciente
    paciente_selecionado = {"id": None, "nome": ""}
    
    def buscar_paciente():
        nome = nome_busca_entry.get()
        pacientes = buscar_paciente_por_nome(nome)
        
        if len(pacientes) == 0:
            resultado_label.configure(text="❌ Paciente não encontrado", text_color="#f87171")
            paciente_selecionado["id"] = None
        elif len(pacientes) == 1:
            p = pacientes[0]
            paciente_selecionado["id"] = p.id
            paciente_selecionado["nome"] = p.nome
            resultado_label.configure(text=f"✓ {p.nome} || CPF: {p.cpf}", text_color="#4ade80")
            atualizar_lista()
        else:
            resultado_label.configure(text=f"⚠ {len(pacientes)} resultados. Seja mais específico.", text_color="#fbbf24")
    
    ctk.CTkButton(frame_busca_linha, text="Buscar", command=buscar_paciente, width=80, height=35, fg_color="#2b2b2b", hover_color="#3a3a3a").grid(row=0, column=1, sticky="e")
    
    # Separador sutil interno para quebrar o visual de bloco único acumulado
    ctk.CTkFrame(frame_formulario, fg_color="#242528", height=1).pack(fill="x", padx=30, pady=(5, 15))

    # [GRUPO 2]: PROCEDIMENTO E ASSISTENTE DE HORÁRIO
    # Tratamento dropdown (Movido para o frame_formulario)
    tratamentos_db = listar_tratamentos()
    tratamentos_lista = [t.nome for t in tratamentos_db]
    
    tratamento_dropdown = ctk.CTkComboBox(
        frame_formulario,
        values=tratamentos_lista,
        width=280,
        height=35,
        fg_color="#2b2b2b",
        button_color="#3a3a3a"
    )
    tratamento_dropdown.pack(pady=(0, 15))
    tratamento_dropdown.set("Selecione o tratamento")
    
    # Bloco dinâmico de tempo (Campos de verificação agrupados por proximidade)
    # Data (Movido para o frame_formulario)
    data_entry = ctk.CTkEntry(frame_formulario, width=280, height=35, placeholder_text="Data (DD/MM/AAAA)", fg_color="#2b2b2b")
    data_entry.pack(pady=(0, 4))

    # Botão de verificar disponibilidade posicionado de forma elegante abaixo da data
    ctk.CTkButton(
        frame_formulario, 
        text="🔍 Verificar Horários Disponíveis", 
        command=lambda: filtrar_horarios_livres(), 
        width=280, 
        fg_color="#1f6aa5", 
        hover_color="#144870",
        font=("Segoe UI", 12, "bold"),
        height=32
    ).pack(pady=(0, 4))

    # horario (Movido para o frame_formulario)
    horario_dropdown = ctk.CTkComboBox(frame_formulario, values=horarios_padrao, width=280, height=35, fg_color="#2b2b2b", button_color="#3a3a3a")
    horario_dropdown.configure(values=horarios_padrao)
    horario_dropdown.pack(pady=(0, 20))
    horario_dropdown.set("Selecione o horário")

    # [GRUPO 3]: FINANCEIRO E FECHAMENTO
    # Valor (Movido para o frame_formulario)
    valor_entry = ctk.CTkEntry(frame_formulario, width=280, height=35, placeholder_text="Valor (ex: 150.00)", fg_color="#2b2b2b")
    valor_entry.pack(pady=(0, 6))
    
    # Método de pagamento dropdown (Movido para o frame_formulario)
    metodo_dropdown = ctk.CTkComboBox(
        frame_formulario,
        values=["Pix", "Débito", "Crédito", "Dinheiro", "Pendente"],
        width=280,
        height=35,
        fg_color="#2b2b2b",
        button_color="#3a3a3a"
    )
    metodo_dropdown.pack(pady=(0, 5))
    metodo_dropdown.set("Método de pagamento")

    def filtrar_horarios_livres():
        data_str = data_entry.get()
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            resultado_label.configure(text="❌ Data inválida. Use DD/MM/AAAA", text_color="#f87171")
            return
        consultas_dia = listar_consultas_data(data.strftime('%Y-%m-%d'))
        horarios_disponiveis = horarios_padrao.copy()
        for i in consultas_dia:
            horario_ocupado = i.data.strftime('%H:%M')
            if horario_ocupado in horarios_disponiveis:
                horarios_disponiveis.remove(horario_ocupado)
        horario_dropdown.configure(values=horarios_disponiveis)
        horario_dropdown.set("Selecione o horário")

    def agendar():
        if paciente_selecionado["id"] is None:
            resultado_label.configure(text="❌ Selecione um paciente primeiro", text_color="#f87171")
            return
        
        tratamento = tratamento_dropdown.get()
        data_str = data_entry.get()
        horario_str = horario_dropdown.get()
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            resultado_label.configure(text="❌ Data inválida. Use DD/MM/AAAA", text_color="#f87171")
            return
        try:
            horario = datetime.strptime(horario_str, "%H:%M").time()
        except ValueError:
            resultado_label.configure(text="❌ Horário Inválido. Use HH:MM", text_color="#f87171")
            return

        data_e_horario = datetime.combine(data.date(), horario)
        
        valor = valor_entry.get()
        metodo = metodo_dropdown.get()
        
        try:
            criar_consulta(paciente_selecionado["id"], tratamento, data_e_horario, valor, metodo)
            atualizar_lista()
            # Limpa os campos
            paciente_selecionado["id"] = None
            paciente_selecionado["nome"] = ""
            nome_busca_entry.delete(0, "end")
            tratamento_dropdown.set("Selecione o tratamento")
            data_entry.delete(0, "end")
            horario_dropdown.set("Selecione o horário")
            valor_entry.delete(0, "end")
            metodo_dropdown.set("Método de pagamento")
            # resposta
            resultado_label.configure(text=f"✓ Consulta agendada com sucesso!", text_color="#4ade80")
        except Exception as e:
            resultado_label.configure(text=f"❌ Erro ao agendar: {str(e)}", text_color="#f87171")

    # Botão de confirmação com folga isolada no topo para dar imponência à ação final
    ctk.CTkButton(
        frame_formulario, 
        text="Confirmar Agendamento", 
        command=agendar, 
        width=280, 
        fg_color="#2b7a3e", 
        hover_color="#1e542b",
        font=("Segoe UI", 13, "bold"),
        height=40
    ).pack(pady=(25, 20))
    
    # --- ELEMENTOS DO HISTÓRICO (DIREITA) ---
    # lista consultas do paciente (Movido para o frame_historico à direita)
    lista_label = ctk.CTkLabel(frame_historico, text="Histórico do Paciente", font=("Segoe UI", 16, "bold"), text_color="#a0a0a5")
    lista_label.pack(pady=(15, 10))
    
    # Tornamos o frame de rolagem totalmente responsivo para preencher o lado direito
    lista_frame = ctk.CTkScrollableFrame(frame_historico, fg_color="transparent", label_text="")
    lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def atualizar_lista():
        # 1. Limpa todas as labels antigas antes de desenhar as novas
        for componente in lista_frame.winfo_children():
            componente.destroy()
            
        # 2. Busca e renderiza a lista atualizada
        lista_label.configure(text=f"Histórico: {paciente_selecionado['nome']}", text_color="#ffffff")
        consultas = listar_consultas_paciente(paciente_selecionado["id"])
        for c in consultas:
            # .strftime("%H:%M") extrai apenas as horas e minutos da sua data unificada
            texto = f"Procedimento: {c.tratamento}\nData: {c.data.strftime('%d/%m/%Y')} às {c.data.strftime('%H:%M')}\nValor: R$ {c.valor} ({c.metodo_pagamento})"
            
            # Criamos um mini card para cada consulta do histórico ficar linda na direita (Combinando com as bordas neutras da agenda)
            card_historico = ctk.CTkFrame(lista_frame, fg_color="#212225", border_width=1, border_color="#3a3a3a", corner_radius=8)
            card_historico.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(
                card_historico, 
                text=texto, 
                justify="left", 
                font=("Segoe UI", 12), 
                text_color="#cfd0d4"
            ).pack(anchor="w", padx=12, pady=10)

    # Bloqueio de segurança inicial para a lista não tentar buscar ID nulo ao abrir a tela
    if paciente_selecionado["id"] is not None:
        atualizar_lista()