import customtkinter as ctk
from database.models import criar_paciente, listar_pacientes, buscar_paciente_por_nome

# parent: É o local (como a janela principal ou uma aba) onde as telas serao desenhadas.
def mostrar(parent):
    titulo = ctk.CTkLabel(parent, text="Pacientes", font=("Arial", 24, "bold"))
    titulo.pack(pady=20)
    
    nome_entry = ctk.CTkEntry(
        parent,
        width=250, 
        placeholder_text="Nome paciente"
    )
    nome_entry.pack(pady=5)
    
    telefone_entry = ctk.CTkEntry(
        parent,
        width=250,
        placeholder_text="Telefone"
    )
    telefone_entry.pack(pady=5)
    
    cpf_entry = ctk.CTkEntry(
        parent,
        width=250,
        placeholder_text="CPF"
    )
    cpf_entry.pack(pady=5)

    # Lista de pacientes
    lista_label = ctk.CTkLabel(parent, text="Pacientes Cadastrados", font=("Arial", 16))
    lista_label.pack(pady=(30, 10))
    
    lista_frame = ctk.CTkScrollableFrame(parent, width=600, height=200)
    lista_frame.pack(pady=10)
    
    def atualizar_lista():
        for widget in lista_frame.winfo_children():
            widget.destroy()
        
        pacientes = listar_pacientes()
        for p in pacientes:
            texto = f"Nome: {p.nome} | Telefone: {p.telefone} | CPF: {p.cpf}"
            ctk.CTkLabel(lista_frame, text=texto).pack(anchor="w", padx=10, pady=5)
    
    def validar():
        if nome_entry.get() == "" or cpf_entry.get() == "" or telefone_entry.get() == "":
            return False
        else:
            return True
    
    def cadastrar():
        if validar():
            nome = nome_entry.get()
            cpf = cpf_entry.get()
            telefone = telefone_entry.get()
            criar_paciente(nome, telefone, cpf)  # ordem correta
            nome_entry.delete(0, "end")
            cpf_entry.delete(0, "end")
            telefone_entry.delete(0, "end")
            atualizar_lista()
        else:
            for componente in lista_frame.winfo_children():
                componente.destroy()
            print("dados invalidos")
            texto = "Dados invalidos"
            ctk.CTkLabel(lista_frame, text=texto).pack(anchor="w", padx=10, pady=5)
        

    # busca_label = ctk.CTkLabel(parent, text="Paciente Encontrado:", font=("Arial", 16))
    # busca_label.pack(pady = 10)

    # busca_frame = ctk.CTkScrollableFrame(parent, width=600, height=200)
    # busca_frame.pack(pady=10)

    # def buscar():
    #     nome = nome_entry.get()
    #     paciente_encontrado = buscar_paciente_por_nome(nome)
    #     if len(paciente_encontrado) != 0:
    #         texto = f"Nome: {paciente_encontrado.nome} | Telefone: {paciente_encontrado.telefone} | CPF: {paciente_encontrado.cpf}"
    #         ctk.CTkLabel(busca_frame, text = texto).pack(anchor="w", padx=10, pady=5)
    #     else:
    #         busca_frame.configure(text="❌ Paciente não encontrado")
        
    
    ctk.CTkButton(
        parent,
        text="Cadastrar",
        command=cadastrar
    ).pack(pady=10)

    # ctk.CTkButton(
    #     parent,
    #     text="buscar",
    #     command=buscar
    # ).pack(pady=10)

    
    atualizar_lista()