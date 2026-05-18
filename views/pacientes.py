import customtkinter as ctk
from database.models import criar_paciente, listar_pacientes

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
    
    def cadastrar():
        nome = nome_entry.get()
        cpf = cpf_entry.get()
        telefone = telefone_entry.get()
        criar_paciente(nome, telefone, cpf)  # ordem correta
        nome_entry.delete(0, "end")
        cpf_entry.delete(0, "end")
        telefone_entry.delete(0, "end")
        atualizar_lista()
    def buscar():
        nome = nome_entry.get()
        
        
    
    ctk.CTkButton(
        parent,
        text="Cadastrar",
        command=cadastrar
    ).pack(pady=10)
    ctk.CTkButton(
        parent,
        text="buscar",
        command=buscar
    ).pack(pady=10)

    
    atualizar_lista()