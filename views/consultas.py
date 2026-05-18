import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_paciente, listar_tratamentos, buscar_paciente_por_nome
from datetime import datetime

def mostrar(parent):
    titulo = ctk.CTkLabel(parent, text="Consultas", font=("Arial", 24, "bold"))
    titulo.pack(pady=20)
    
    # Buscar paciente por nome
    nome_busca_entry = ctk.CTkEntry(parent, width=250, placeholder_text="Nome do paciente")
    nome_busca_entry.pack(pady=5)
    
    resultado_label = ctk.CTkLabel(parent, text="", font=("Arial", 12))
    resultado_label.pack(pady=5)

    paciente_selecionado = {"id": None, "nome": ""}
    
    def buscar_paciente():
        nome = nome_busca_entry.get()
        pacientes = buscar_paciente_por_nome(nome)
        
        if len(pacientes) == 0:
            resultado_label.configure(text="❌ Paciente não encontrado")
            paciente_selecionado["id"] = None
        elif len(pacientes) == 1:
            p = pacientes[0]
            paciente_selecionado["id"] = p.id
            paciente_selecionado["nome"] = p.nome
            resultado_label.configure(text=f"✓ {p.nome} || CPF: {p.cpf}")
        else:
            resultado_label.configure(text=f"⚠ {len(pacientes)} pacientes encontrados. Seja mais específico.")
    
    ctk.CTkButton(parent, text="Buscar", command=buscar_paciente, width=100).pack(pady=5)
    
    # Tratamento dropdown
    tratamentos_db = listar_tratamentos()
    tratamentos_lista = [t.nome for t in tratamentos_db]
    
    tratamento_dropdown = ctk.CTkComboBox(
        parent,
        values=tratamentos_lista,
        width=250
    )
    tratamento_dropdown.pack(pady=5)
    tratamento_dropdown.set("Selecione o tratamento")
    
    # Data
    data_entry = ctk.CTkEntry(parent, width=250, placeholder_text="Data (DD/MM/AAAA)")
    data_entry.pack(pady=5)
    
    # Valor
    valor_entry = ctk.CTkEntry(parent, width=250, placeholder_text="Valor (ex: 150.00)")
    valor_entry.pack(pady=5)
    
    # Método de pagamento dropdown
    metodo_dropdown = ctk.CTkComboBox(
        parent,
        values=["Pix", "Débito", "Crédito", "Dinheiro", "Pendente"],
        width=250
    )
    metodo_dropdown.pack(pady=5)
    metodo_dropdown.set("Método de pagamento")
    
    def agendar():
        if paciente_selecionado["id"] is None:
            resultado_label.configure(text="❌ Selecione um paciente primeiro")
            return
        
        tratamento = tratamento_dropdown.get()
        data_str = data_entry.get()
        data = datetime.strptime(data_str, "%d/%m/%Y")
        valor = valor_entry.get()
        metodo = metodo_dropdown.get()

        criar_consulta(paciente_selecionado["id"],tratamento, data, valor, metodo)

        paciente_selecionado.delete(0, "end")
        tratamento_dropdown.delete(0, "end")
        valor_entry.delete(0, "end")
        metodo_dropdown.delete(0, "end")
        
        resultado_label.configure(text=f"✓ Consulta agendada para {paciente_selecionado['nome']}")
    
    ctk.CTkButton(parent, text="Agendar Consulta", command=agendar).pack(pady=20)