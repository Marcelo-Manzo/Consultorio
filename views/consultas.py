import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_paciente

def mostrar(parent):
    titulo = ctk.CTkLabel(parent, text="Consultas", font=("Arial", 24, "bold"))
    titulo.pack(pady=20)
    
    paciente_id_entry = ctk.CTkEntry(
        parent,
        width=250, 
        placeholder_text="ID do paciente"
    )
    paciente_id_entry.pack(pady=5)
    
    tratamento_entry = ctk.CTkEntry(
        parent,
        width=250,
        placeholder_text="Tratamento"
    )
    tratamento_entry.pack(pady=5)
    
    data_entry = ctk.CTkEntry(
        parent,
        width=250,
        placeholder_text="Data (YYYY-MM-DD)"
    )
    data_entry.pack(pady=5)

    valor_entry = ctk.CTkEntry(
        parent,
        width=250,
        placeholder_text="Valor"
    )
    valor_entry.pack(pady=5)

    metodo_pagamento_entry = ctk.CTkEntry(
        parent,
        width=250,
        placeholder_text="Método de pagamento"
    )
    metodo_pagamento_entry.pack(pady=5)