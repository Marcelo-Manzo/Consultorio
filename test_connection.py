from database.models import criar_paciente, listar_pacientes

# Testa criar um paciente
print("Criando paciente de teste...")
criar_paciente("Marcelo Manzo", "19993678862", "987.654.321-00")

# Testa listar
print("\nListando pacientes:")
pacientes = listar_pacientes()
for p in pacientes:
    print(f"ID : {p.id} | nome: {p.nome}| cpf: {p.cpf}")

# pacientes = listar_pacientes()
# for p in pacientes:
#     print(f"ID: {p.id} | Nome: {p.nome} | CPF: {p.cpf}")