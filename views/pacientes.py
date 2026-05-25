import customtkinter as ctk
from database.models import criar_paciente, listar_pacientes, buscar_paciente_por_nome

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
    
    def atualizar_lista():
        for widget in lista_frame.winfo_children():
            widget.destroy()
        
        pacientes = listar_pacientes()
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
    
    def validar():
        if nome_entry.get() == "" or cpf_entry.get() == "" or telefone_entry.get() == "":
            return False
        return True
    
    def cadastrar():
        if validar():
            nome = nome_entry.get()
            cpf = cpf_entry.get()
            telefone = telefone_entry.get()
            criar_paciente(nome, telefone, cpf)  # ordem correta
            
            # Limpa os campos após o sucesso
            nome_entry.delete(0, "end")
            cpf_entry.delete(0, "end")
            telefone_entry.delete(0, "end")
            
            resultado_label.configure(text="✓ Paciente cadastrado com sucesso!", text_color="#4ade80")
            atualizar_lista()
        else:
            resultado_label.configure(text="❌ Preencha todos os campos obrigatórios.", text_color="#f87171")
        
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
    ).pack(pady=(25, 20))

    # Inicializa a lista ao abrir a tela
    atualizar_lista()