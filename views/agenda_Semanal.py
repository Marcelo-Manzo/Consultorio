import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_data, buscar_paciente_por_id, deletar_consulta, update_consulta,listar_tratamentos
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
    
    def abrir_janela_editar(consulta):
        frame_editar_consulta = ctk.CTkToplevel(parent, fg_color="#2b2b2b")
        frame_editar_consulta.title("Editar Consulta") # Dá um título bonito para ela
        
        # 1. Defina o tamanho que você quer para a janela de edição
        largura_janela = 400
        altura_janela = 300

        # 2. Descobre o tamanho total da tela do computador do usuário
        largura_tela = frame_editar_consulta.winfo_screenwidth()
        altura_tela = frame_editar_consulta.winfo_screenheight()

        # 3. Faz a matemática para descobrir onde fica o centro da tela
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        # 4. Aplica a geometria final no formato: LARGURAxALTURA+X+Y
        frame_editar_consulta.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")

        # 5. Segurança: Faz a janela ficar sempre na frente e impede cliques fora dela até ser fechada
        frame_editar_consulta.grab_set()

        #====================CustomTkinter======================
        # Tratamento dropdown
        tratamentos_db = listar_tratamentos()
        tratamentos_lista = [t.nome for t in tratamentos_db]
        
        tratamento_dropdown = ctk.CTkComboBox(
            frame_editar_consulta,
            values=tratamentos_lista,
            width=250
        )
        tratamento_dropdown.pack(pady=5)
        tratamento_dropdown.set("Selecione o tratamento")

        data_entry = ctk.CTkEntry(frame_editar_consulta, width=250, placeholder_text="Data (DD/MM/AAAA)")
        data_entry.pack(pady=3)
        data_entry.insert(0, consulta.data.strftime('%d/%m/%Y')) 

        horario_entry = ctk.CTkEntry(frame_editar_consulta, width=250, placeholder_text="Horário")
        horario_entry.pack(pady=3)
        horario_entry.insert(0, consulta.data.strftime('%H:%M'))

        valor_entry = ctk.CTkEntry(frame_editar_consulta, width=250, placeholder_text="Valor (ex: 150.00)")
        valor_entry.pack(pady=5)
        valor_entry.insert(0, consulta.valor)

        metodo_dropdown = ctk.CTkComboBox(
        frame_editar_consulta,
        values=["Pix", "Débito", "Crédito", "Dinheiro", "Pendente"],
        width=250
        )
        metodo_dropdown.pack(pady=5)
        metodo_dropdown.set("Método de pagamento")

        resultado_editar_label = ctk.CTkLabel(frame_editar_consulta, text="", font=("Arial", 12))
        resultado_editar_label.pack(pady=5)
        #====================== variaveis=====================

        def realizar_update():
            # A captura dos dados (.get())
            novo_tratamento = tratamento_dropdown.get()
            data_str = data_entry.get()
            horario_str = horario_entry.get()
            novo_valor = valor_entry.get()
            novo_metodo = metodo_dropdown.get()

            # Converter as strings digitadas em objetos reais (Igual você fez na tela de agendar)
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                horario_obj = datetime.strptime(horario_str, "%H:%M").time()
                data_e_horario_final = datetime.combine(data_obj.date(), horario_obj)
                resultado_editar_label.configure(text="✓Consulta Atualizada")
            except ValueError:
                resultado_editar_label.configure(text="❌ Data ou Horário inválidos.")
                return

            # Executa a função do banco passando os novos dados
            update_consulta(consulta.id, novo_tratamento, data_e_horario_final, novo_valor, novo_metodo)
            # Fecha a janelinha de edição automaticamente
            frame_editar_consulta.destroy()

            # Atualiza a agenda da tela principal para mostrar os novos dados na hora!
            redesenhar_agenda()

        ctk.CTkButton(frame_editar_consulta, text="Salvar", command=realizar_update).pack(pady=20)

    # Título da tela 
    titulo = ctk.CTkLabel(parent, font=("Arial", 24, "bold"))
    titulo.pack(pady=20)

    # Frame para agrupar os botões lado a lado no topo
    frame_botoes = ctk.CTkFrame(parent, fg_color="transparent")
    frame_botoes.pack(pady=10)

    # Botões de navegação passados SEM parênteses no 'command'
    ctk.CTkButton(frame_botoes, text="<<", command=retroceder_semana, width=60).pack(side="left", padx=5)
    ctk.CTkButton(
    frame_botoes, 
    text="🏠", 
    # Trocamos o sinal de igual por .update() para o Python aceitar a instrução
    command=lambda: [controle_semana.update({"deslocamento": 0}), redesenhar_agenda()], 
    width=60
    ).pack(side="left", padx=5)
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
                texto_linha = f"{consulta.data.strftime('%H:%M')}\n - {p.nome} \n- {consulta.tratamento}"
                
                # Mudado para .grid() para fixar o alinhamento esquerdo e adicionado wraplength para evitar deformações
                lbl_item = ctk.CTkLabel(consulta_frame, text=texto_linha, justify="left", font=("Arial", 16), wraplength=130)
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
                ctk.CTkButton(
                    consulta_frame, 
                    text="✏️", 
                    command=lambda c=consulta: [abrir_janela_editar(c)], 
                    width=28,
                    height=28,
                    corner_radius=6,          # Deixa os cantos do botão levemente arredondados
                    fg_color="#053614",        # Vermelho bem escuro (simula o vermelho transparente sobre o fundo cinza)
                    hover_color="#3a6b3e",     # Vermelho um pouco mais vivo quando o mouse passa por cima
                    text_color="#ffffff"       # Garante que o X fique totalmente branco
                ).grid(row=1, column=1, sticky="e", padx=10, pady=8) # Mudado para .grid() para fixar no canto direito