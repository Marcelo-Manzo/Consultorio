import customtkinter as ctk
from validate_docbr import CPF
import re
from database.models import criar_paciente, listar_pacientes, buscar_paciente_por_nome, buscar_paciente_por_cpf

# parent: É o local (como a janela principal ou uma aba) onde as telas serao desenhadas.
def mostrar(parent):
    titulo = ctk.CTkLabel(parent, text="Controle de Pacientes", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    titulo.pack(pady=(20, 10))
    
    # CONTAINER CENTRAL: Divide a tela em duas colunas paralelas (Formulário na esquerda, Lista na direita)
    container_principal = ctk.CTkFrame(parent, fg_color="transparent")
    container_principal.pack(fill="both", expand=True, padx=20, pady=10)
    container_principal.columnconfigure(0, weight=1, uniform="coluna")
    container_principal.columnconfigure(1, weight=1, uniform="coluna")
    container_principal.rowconfigure(0, weight=1)

    # SUB-FRAME ESQUERDO: Guarda todos os campos de cadastro (Estilizado como bloco Premium)
    frame_formulario = ctk.CTkFrame(container_principal, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
    frame_formulario.grid(row=0, column=0, sticky="nsew", padx=15, pady=5)

    # SUB-FRAME DIREITO: Guarda a lista de pacientes cadastrados
    frame_lista = ctk.CTkFrame(container_principal, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
    frame_lista.grid(row=0, column=1, sticky="nsew", padx=15, pady=5)

    # --- ELEMENTOS DO FORMULÁRIO (ESQUERDA) ---
    lbl_secao_form = ctk.CTkLabel(frame_formulario, text="Cadastrar Novo Paciente", font=("Segoe UI", 16, "bold"), text_color="#ffffff")
    lbl_secao_form.pack(pady=(20, 15))

    # Campos de texto movidos para o frame_formulario (Com tamanho e respiro calibrados)
    nome_entry = ctk.CTkEntry(frame_formulario, width=280, height=35, placeholder_text="Nome do paciente", fg_color="#2b2b2b")
    nome_entry.pack(pady=6)
    
    telefone_entry = ctk.CTkEntry(frame_formulario, width=280, height=35, placeholder_text="Telefone", fg_color="#2b2b2b")
    telefone_entry.pack(pady=6)
    
    cpf_entry = ctk.CTkEntry(frame_formulario, width=280, height=35, placeholder_text="CPF", fg_color="#2b2b2b")
    cpf_entry.pack(pady=6)

    # Label sutil para avisos de validação / feedbacks
    resultado_label = ctk.CTkLabel(frame_formulario, text="", font=("Segoe UI", 12))
    resultado_label.pack(pady=(5, 0))

    # Lista de pacientes movida para o frame_lista à direita
    lista_label = ctk.CTkLabel(frame_lista, text="Pacientes Cadastrados", font=("Segoe UI", 16, "bold"), text_color="#a0a0a5")
    lista_label.pack(pady=(15, 10))
    
    # Tornamos o frame de rolagem totalmente responsivo para preencher o lado direito
    lista_frame = ctk.CTkScrollableFrame(frame_lista, fg_color="transparent", label_text="")
    lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # MODIFICAÇÃO: Agora aceita receber uma lista vinda de fora (como o resultado da busca)
    def atualizar_lista(lista_filtrada=None):
        for widget in lista_frame.winfo_children():
            widget.destroy()
        
        # Se recebeu uma lista da busca, usa ela. Se não, lista todos do banco.
        pacientes = lista_filtrada if lista_filtrada is not None else listar_pacientes()
        
        for p in pacientes:
            texto = f"Nome: {p.nome}\nTelefone: {p.telefone} | CPF: {p.cpf}"
            
            # Criamos um mini card arredondado para cada paciente do histórico ficar elegante (Borda sutil neutra)
            card_paciente = ctk.CTkFrame(lista_frame, fg_color="#212225", border_width=1, border_color="#3a3a3a", corner_radius=8)
            card_paciente.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(
                card_paciente, 
                text=texto, 
                justify="left", 
                font=("Segoe UI", 12), 
                text_color="#cfd0d4"
            ).pack(anchor="w", padx=12, pady=10)


    # =============================================================================
    # MÁSCARAS DINÂMICAS (FORMATAM ENQUANTO DIGITA)
    # =============================================================================
    def aplicar_mascara_cpf(event):
        widget = event.widget
        texto_atual = widget.get()

        # Extrai apenas números e limita a 11 dígitos
        numeros = re.sub(r"\D", "", texto_atual)[:11]

        cpf_formatado = ""
        for i, char in enumerate(numeros):
            if i in (3, 6):
                cpf_formatado += "."
            elif i == 9:
                cpf_formatado += "-"
            cpf_formatado += char

        if texto_atual != cpf_formatado:
            widget.delete(0, "end")
            widget.insert(0, cpf_formatado)


    def aplicar_mascara_telefone(event):
        widget = event.widget
        texto_atual = widget.get()

        # Extrai apenas números e limita a 11 dígitos (celular)
        numeros = re.sub(r"\D", "", texto_atual)[:11]

        tel_formatado = ""
        for i, char in enumerate(numeros):
            if i == 0:
                tel_formatado += "("
            elif i == 2:
                tel_formatado += ") "
            elif len(numeros) <= 10 and i == 6:  # Telefone Fixo: (XX) XXXX-XXXX
                tel_formatado += "-"
            elif len(numeros) == 11 and i == 7:  # Celular: (XX) XXXXX-XXXX
                tel_formatado += "-"
            tel_formatado += char

        if texto_atual != tel_formatado:
            widget.delete(0, "end")
            widget.insert(0, tel_formatado)


    # =============================================================================
    # FUNÇÕES DE VALIDAÇÃO
    # =============================================================================
    def eh_telefone_valido(telefone: str) -> bool:
        # 1. Remove tudo que não for dígito
        numeros = re.sub(r"\D", "", telefone)

        # 2. Verifica se o tamanho corresponde a Fixos (10 dígitos) ou Celulares (11 dígitos)
        if len(numeros) not in (10, 11):
            return False

        # 3. Impede sequências repetidas inválidas (ex: 11111111111)
        if len(set(numeros)) == 1:
            return False

        # 4. Se for celular (11 dígitos), verifica se o DDD é válido e o 3º dígito é '9'
        if len(numeros) == 11:
            ddd = int(numeros[:2])
            if ddd < 11 or ddd > 99 or ddd % 10 == 0:
                return False

            if numeros[2] != "9":
                return False

        return True


    def validar():
        cpf_validator = CPF()
        # 1. Pega os valores limpos
        nome = nome_entry.get().strip()
        cpf_str = cpf_entry.get().strip()
        telefone = telefone_entry.get().strip()

        # 2. Validação do Nome
        if not nome:
            resultado_label.configure(
                text="❌ Insira um nome", text_color="#f87171"
            )
            return False

        # 3. Validação do Telefone
        if not eh_telefone_valido(telefone):
            resultado_label.configure(
                text="❌ Telefone inválido", text_color="#f87171"
            )
            return False

        # 4. Validação do CPF
        if not cpf_validator.validate(cpf_str) or not cpf_str:
            resultado_label.configure(
                text="❌ CPF inválido", text_color="#f87171"
            )
            return False
        if len(buscar_paciente_por_cpf(cpf_str)):
            resultado_label.configure(
                text="❌ Ja existe um paciente com esse CPF", text_color="#f87171"
            )
            return False

        # Sucesso
        resultado_label.configure(
            text="✓ Cadastrado com sucesso!", text_color="#4ade80"
        )
        return True

    # =============================================================================
    # VINCULANDO OS EVENTOS AOS INPUTS
    # =============================================================================
    # Lembre-se de adicionar o .bind() logo após a criação de cada CTkEntry na sua interface:

    cpf_entry.bind("<KeyRelease>", aplicar_mascara_cpf)
    telefone_entry.bind("<KeyRelease>", aplicar_mascara_telefone)

    
    def cadastrar():
        if validar():
            nome = nome_entry.get().strip()
            cpf = cpf_entry.get().strip()
            telefone = telefone_entry.get().strip()
            criar_paciente(nome, telefone, cpf)  # ordem correta
            
            # Limpa os campos após o sucesso
            nome_entry.delete(0, "end")
            cpf_entry.delete(0, "end")
            telefone_entry.delete(0, "end")
            
            resultado_label.configure(text="✓ Paciente cadastrado com sucesso!", text_color="#4ade80")
            atualizar_lista()  # Recarrega trazendo todo mundo
        
    def buscar_paciente():
        nome_busca = nome_entry.get().strip()
        
        # Se o campo de busca NÃO estiver vazio, filtra no banco
        if nome_busca:
            pacientes_encontrados = buscar_paciente_por_nome(nome_busca)
            
            if not pacientes_encontrados:
                resultado_label.configure(text="❌ Nenhum paciente encontrado com esse nome.", text_color="#f87171")
                # Limpa a lista da direita para dar o feedback visual de vazio
                atualizar_lista([]) 
                return
            
            # Renderiza a lista passando apenas os encontrados
            atualizar_lista(pacientes_encontrados)
            resultado_label.configure(text=f"🔍 Encontrado(s) {len(pacientes_encontrados)} paciente(s).", text_color="#4ade80")
            
        else:
            # Se clicar em buscar com o campo vazio, reseta e mostra todo mundo de novo
            atualizar_lista()
            resultado_label.configure(text="✓ Listando todos os pacientes.", text_color="#9ca3af")

    # Botão de cadastrar movido para o frame_formulario, com cores correspondentes e folga no topo
    ctk.CTkButton(
        frame_formulario,
        text="Cadastrar Paciente",
        command=cadastrar,
        width=280,
        height=40,
        font=("Segoe UI", 13, "bold"),
        fg_color="#2b7a3e",
        hover_color="#1e542b"
    ).pack(pady=(25, 10)) # Reduzido o pady inferior para aproximar os botões

    ctk.CTkButton(
        frame_formulario,
        text="Buscar por Nome",
        command=buscar_paciente,
        width=280,
        height=40,
        font=("Segoe UI", 13, "bold"),
        fg_color="#005688",
        hover_color="#043D5E"
    ).pack(pady=(0, 20))

    # Inicializa a lista ao abrir a tela
    atualizar_lista()