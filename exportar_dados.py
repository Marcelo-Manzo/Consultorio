from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import sessionmaker

from database import models
from database.connection import DATABASE_URL

# URL do Supabase (preencha no .env: SUPABASE_URL=postgresql://...)
SUPABASE_URL = None
try:
    from dotenv import load_dotenv
    import os

    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
except Exception:
    pass

if not SUPABASE_URL:
    print("❌ Variável SUPABASE_URL não encontrada no .env.")
    print("Adicione no .env: SUPABASE_URL=postgresql://postgres:SUA_SENHA@db.xxxx.supabase.co:5432/postgres")
    raise SystemExit(1)

# ==================== CONEXÕES ====================
print("Conectando ao SQL Server (origem)...")
engine_origem = create_engine(DATABASE_URL)
print("Conectando ao Supabase (destino)...")
engine_destino = create_engine(SUPABASE_URL)

Sessao_origem = sessionmaker(bind=engine_origem)
Sessao_destino = sessionmaker(bind=engine_destino)

# ==================== MAPEAMENTO: ordem importa (FKs) ====================
TABELAS = [
    (models.Paciente, "Pacientes"),
    (models.Consulta, "Consultas"),
    (models.Orcamento, "Orcamentos"),
    (models.Tratamento, "Tratamentos"),
    (models.Usuario, "Usuarios"),
]


def _copiar_tabela(modelo, nome_tabela):
    print(f"\n>>> Copiando {nome_tabela}...")
    with Sessao_origem() as src:
        registros = src.scalars(select(modelo)).all()
    print(f"    Origem (SQL Server): {len(registros)} registros")

    qtd_inseridos = 0
    with Sessao_destino() as dst:
        for reg in registros:
            novo = modelo(id=reg.id)
            for col in modelo.__table__.columns.keys():
                if col != "id":
                    setattr(novo, col, getattr(reg, col))
            dst.merge(novo)
            qtd_inseridos += 1
        dst.commit()
    print(f"    Destino (Supabase): {qtd_inseridos} inseridos/atualizados")


def main():
    # Limpa os dados atuais do destino para evitar duplicatas
    print("\nLimpando tabelas existentes no Supabase...")
    with engine_destino.connect() as conn:
        for _, nome in reversed(TABELAS):
            try:
                conn.execute(text(f'DELETE FROM "{nome}"'))
                print(f"    - {nome} limpa")
            except Exception as e:
                print(f"    - {nome}: erro ao limpar ({e})")
        conn.commit()

    for modelo, nome in TABELAS:
        _copiar_tabela(modelo, nome)

    print("\n✅ Migração concluída!")


if __name__ == "__main__":
    main()