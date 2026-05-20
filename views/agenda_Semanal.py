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
    #rowConfigure Faz exatamente a mesma coisa que o columnconfigure, mas olhando para a Linha 0. Diz para a linha do calendário esticar e ocupar a tela inteira de cima a baixo na vertical.
    # Descobre a segunda-feira da semana atual como ponto de partida
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    
    dias_nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # Loop para renderizar os 5 dias úteis lado a lado
    for i in range(5):

        # Define larguras iguais para todas as colunas
        frame_calendario.columnconfigure(i, weight=1, uniform="col")
        # columnconfigure(i, ...): Avisa ao Python que estamos configurando as propriedades da coluna número i.weight=1: É a propriedade mais importante do grid. Ela funciona como um elástico. Se a janela aumentar de tamanho, as colunas que têm weight=1 vão esticar para preencher o espaço. Se você esquecer o weight, a coluna fica travada com tamanho zero ou esmagada.uniform="col": Força todas as colunas que tiverem esse mesmo nome (no caso, "col") a terem rigorosamente a mesma largura. Isso impede que o container de "Segunda" fique maior do que o de "Terça" só porque tem mais texto escrito nele.


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
            # Se p for uma lista vinda do fetchall(), pegamos o primeiro item da lista usando [0]
            p_lista = buscar_paciente_por_id(consulta.paciente_id)

            # Monta os dados estruturados do paciente na linha de exibição
            if p_lista: # Garante que o banco encontrou o paciente para não quebrar
                p = p_lista[0] 
                texto_linha = f"{consulta.data.strftime('%H:%M')} - {p.nome} - {consulta.tratamento}\n\n"
                lista_consultas.insert("end", texto_linha)
                
        # Trava a edição do campo de texto (somente leitura para exibição)
        lista_consultas.configure(state="disabled")
