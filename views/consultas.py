import customtkinter as ctk
from database.models import criar_consulta, listar_consultas_paciente, listar_tratamentos, buscar_paciente_por_nome
from datetime import datetime

def mostrar(parent):
    titulo = ctk.CTkLabel(parent, text="Consultas", font=("Arial", 24, "bold"))
    titulo.pack(pady=20)
    
    # Buscar paciente por nome
    nome_busca_entry = ctk.CTkEntry(parent, width=250, placeholder_text="Nome do paciente")
    nome_busca_entry.pack(pady=5)
    
    #resposta
    resultado_label = ctk.CTkLabel(parent, text="", font=("Arial", 12))
    resultado_label.pack(pady=5)

    #declaração do paciente
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
            atualizar_lista()
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
        
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            resultado_label.configure(text="❌ Data inválida. Use DD/MM/AAAA")
            return
        
        valor = valor_entry.get()
        metodo = metodo_dropdown.get()
        
        try:
            criar_consulta(paciente_selecionado["id"], tratamento, data, valor, metodo)
            atualizar_lista()
            # Limpa os campos
            paciente_selecionado["id"] = None
            paciente_selecionado["nome"] = ""
            nome_busca_entry.delete(0, "end")
            tratamento_dropdown.set("Selecione o tratamento")
            data_entry.delete(0, "end")
            valor_entry.delete(0, "end")
            metodo_dropdown.set("Método de pagamento")
            #resposta
            resultado_label.configure(text=f"✓ Consulta agendada com sucesso!")
        except Exception as e:
            resultado_label.configure(text=f"❌ Erro ao agendar: {str(e)}")

    ctk.CTkButton(parent, text="Agendar Consulta", command=agendar).pack(pady=20)
    
    #lista consultas do paciente
    lista_label = ctk.CTkLabel(parent, text=f"Consultas Paciente {paciente_selecionado['nome']}", font=("Arial", 16))
    lista_label.pack(pady=(30, 10))
    
    lista_frame = ctk.CTkScrollableFrame(parent, width=600, height=200)
    lista_frame.pack(pady=10)

    def atualizar_lista():
        # 1. Limpa todas as labels antigas antes de desenhar as novas
        for componente in lista_frame.winfo_children():
            componente.destroy()
            
        # 2. Busca e renderiza a lista atualizada
        consultas = listar_consultas_paciente(paciente_selecionado["id"])
        for c in consultas:
            texto = f"tratamento:{c.tratamento} || Dia:{c.data} || valor: {c.valor}"
            ctk.CTkLabel(lista_frame, text=texto).pack(anchor="w", padx=10, pady=5)

    atualizar_lista()