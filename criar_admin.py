import getpass

from database import create_user

nome = input("Nome do admin: ").strip()
email = input("Email: ").strip()
senha = getpass.getpass("Senha: ")

if not nome or not email or not senha:
    print("❌ Nome, email e senha são obrigatórios.")
    raise SystemExit(1)

try:
    create_user(nome, email, senha)
    print(f"✓ Usuário '{email}' criado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")