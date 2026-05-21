import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_data, buscar_paciente_por_id, deletar_consulta
from datetime import datetime, timedelta

# Variável de controle fora da função para reter o valor entre os redesenhos da tela
# 0 = Semana Atual | 1 = Próxima Semana | -1 = Semana Anterior
controle_semana = {"deslocamento": 0}

def mostrar(parent):
    def redesenhar_agenda():
        for widget in parent.winfo_children():
            widget.destroy()
        mostrar(parent)

    # Funções de navegação alterando o estado do deslocamento global
    def avanca_semana():
        controle_semana["deslocamento"] += 1
        redesenhar_agenda()

    def retroceder_semana():
        controle_semana["deslocamento"] -= 1
        redesenhar_agenda()

    # Título da tela
    titulo = ctk.CTkLabel(parent, font=("Arial", 24, "bold"))
    titulo.pack(pady=20)

    # Frame para agrupar os botões lado a lado no topo
    frame_botoes = ctk.CTkFrame(parent, fg_color="transparent")
    frame_botoes.pack(pady=10)

    # Botões de navegação passados SEM parênteses no 'command'
    ctk.CTkButton(frame_botoes, text="<<", command=retroceder_semana, width=60).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text=">>", command=avanca_semana, width=60).pack(side="left", padx=5)

    # Frame container do calendário semanal
    frame_calendario = ctk.CTkFrame(parent, fg_color="transparent")
    frame_calendario.pack(fill="both", expand=True, padx=20, pady=10)

    # Configurações de expansão para habilitar o grid responsivo vertical
    frame_calendario.rowconfigure(0, weight=1)
    #rowConfigure Faz exatamente a mesma coisa que o columnconfigure, mas olhando para a Linha 0. Diz para a linha do calendário esticar e ocupar a tela inteira de cima a baixo na vertical.

    # Descobre a segunda-feira da semana atual e aplica o deslocamento dos botões
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday()) + timedelta(weeks=controle_semana["deslocamento"])

    mes_ano_texto = inicio_semana.strftime("%m/%Y")
    titulo.configure(text=f"Agenda - {mes_ano_texto}")
    
    dias_nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # Loop para renderizar os 5 dias úteis lado a lado
    for i in range(5):
        # Define larguras iguais e responsivas para todas as 5 colunas (.grid)
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

        # Container rolável correto para empilhar os cards de consultas de forma organizada
        lista_consultas = ctk.CTkScrollableFrame(dia_container, fg_color="#1d1e22", label_text="")
        lista_consultas.pack(fill="both", expand=True, padx=5, pady=5)

        # Formata a data atual da coluna para o banco de dados (Ex: "2026-05-18")
        data_banco = data_dia.strftime('%Y-%m-%d')
        
        # Busca apenas as consultas correspondentes a essa data específica
        consultas = listar_consultas_data(data_banco)
        for consulta in consultas:
            p_lista = buscar_paciente_por_id(consulta.paciente_id)

            if p_lista: # Garante que o banco encontrou o paciente para não quebrar
                p = p_lista
                
                # Criamos um CTkFrame interno (o card) arredondado para cada horário
                consulta_frame = ctk.CTkFrame(lista_consultas, fg_color="#2b2b2b", corner_radius=8)
                consulta_frame.pack(fill="x", padx=5, pady=4)
                
                # Configuração de colunas internas para garantir a uniformidade do tamanho do botão
                consulta_frame.columnconfigure(0, weight=1)
                consulta_frame.columnconfigure(1, weight=0)
                
                # Texto formatado dentro do card arredondado
                texto_linha = f"{consulta.data.strftime('%H:%M')} - {p.nome}- {consulta.tratamento}"
                
                # Mudado para .grid() para fixar o alinhamento esquerdo e adicionado wraplength para evitar deformações
                lbl_item = ctk.CTkLabel(consulta_frame, text=texto_linha, justify="left", font=("Arial", 11), wraplength=130)
                lbl_item.grid(row=0, column=0, sticky="w", padx=10, pady=8)

                #botão de excluir consulta
                ctk.CTkButton(
                    consulta_frame, 
                    text="❌", 
                    command=lambda c_id=consulta.id: [deletar_consulta(c_id), redesenhar_agenda()], 
                    width=28,
                    height=28,
                    corner_radius=6,          # Deixa os cantos do botão levemente arredondados
                    fg_color="#4a1515",        # Vermelho bem escuro (simula o vermelho transparente sobre o fundo cinza)
                    hover_color="#7a1f1f",     # Vermelho um pouco mais vivo quando o mouse passa por cima
                    text_color="#ffffff"       # Garante que o X fique totalmente branco
                ).grid(row=0, column=1, sticky="e", padx=10, pady=8) # Mudado para .grid() para fixar no canto direito