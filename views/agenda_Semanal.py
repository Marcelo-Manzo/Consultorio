import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_data, buscar_paciente_por_id, buscar_paciente_por_nome
from datetime import datetime, timedelta

def mostrar(parent):
    # Título da tela
    titulo = ctk.CTkLabel(parent, text="Agenda", font=("Arial", 24, "bold"))
    titulo.pack(pady=20)

    # Frame container do calendário semanal
    frame_calendario = ctk.CTkFrame(parent, fg_color="transparent")
    frame_calendario.pack(fill="both", expand=True, padx=20, pady=10)

    # Configurações de expansão para habilitar o grid responsivo
    frame_calendario.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    # Descobre a segunda-feira da semana atual como ponto de partida
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    
    dias_nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # Loop para renderizar os 5 dias úteis lado a lado
    for i in range(5):
        # Define larguras iguais para todas as colunas
        frame_calendario.columnconfigure(i, weight=1, uniform="col")

        # Calcula a data exata da coluna e monta o cabeçalho
        data_dia = inicio_semana + timedelta(days=i)
        texto_cabecalho = f"{dias_nomes[i]}\n{data_dia.strftime('%d/%m')}"

        # Card visual de fundo para cada dia da semana
        dia_container = ctk.CTkFrame(frame_calendario, border_width=1, border_color="#3a3a3a")
        dia_container.grid(row=0, column=i, sticky="nsew", padx=4, pady=4)
        
        # Nome do dia e data formatada
        lbl_dia = ctk.CTkLabel(dia_container, text=texto_cabecalho, font=("Arial", 14, "bold"))
        lbl_dia.pack(pady=10)

        # Caixa de texto rolável para exibir a lista de agendamentos
        lista_consultas = ctk.CTkTextbox(dia_container, fg_color="#1d1e22", activate_scrollbars=True)
        lista_consultas.pack(fill="both", expand=True, padx=5, pady=5)

        # Formata a data atual da coluna para o banco de dados (Ex: "2026-05-18")
        data_banco = data_dia.strftime('%Y-%m-%d')
        
        # Busca apenas as consultas correspondentes a essa data específica
        consultas = listar_consultas_data(data_banco)
        for consulta in consultas:
            p = buscar_paciente_por_id(consulta.paciente_id)
            
            # Monta os dados estruturados do paciente na linha de exibição
            texto_linha = f"{consulta.horario} - {p.nome}\n- {consulta.tratamento}\n\n"
            lista_consultas.insert("end", texto_linha)
                
        # Trava a edição do campo de texto (somente leitura para exibição)
        lista_consultas.configure(state="disabled")
