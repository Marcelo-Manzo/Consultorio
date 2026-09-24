import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from database import models
from database.connection import DATABASE_URL

# Carrega o .env da raiz do projeto (caminho explícito)
load_dotenv(Path(__file__).resolve().parent / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    print("❌ Variável SUPABASE_URL não encontrada no .env.")
    print("Adicione no .env: SUPABASE_URL=postgresql://...")
    raise SystemExit(1)

# ==================== CONEXÕES ====================
print("Conectando ao SQL Server (origem)...")
engine_origem = create_engine(DATABASE_URL)
print("Conectando ao Supabase (destino)...")
engine_destino = create_engine(SUPABASE_URL, connect_args={"connect_timeout": 15})

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
        # Dono padrão para dados legados (sem usuario_id na origem): o 1º usuário
        id_dono = dst.scalar(select(models.Usuario.id).order_by(models.Usuario.id).limit(1))
        for reg in registros:
            novo = modelo(id=reg.id)
            for col in modelo.__table__.columns.keys():
                if col == "id":
                    continue
                if hasattr(reg, col):
                    # Coluna existe na origem → copia o valor real
                    setattr(novo, col, getattr(reg, col))
                elif col == "usuario_id" and id_dono is not None:
                    # Origem sem multi-usuário → atribui ao 1º usuário do destino
                    novo.usuario_id = id_dono
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
            except Exception as ex:
                print(f"    - {nome}: erro ao limpar ({ex})")
        conn.commit()

    for modelo, nome in TABELAS:
        _copiar_tabela(modelo, nome)

    # Verificação final no Supabase
    print("\n=== VERIFICAÇÃO NO SUPABASE ===")
    with engine_destino.connect() as conn:
        for _, nome in TABELAS:
            qtd = conn.execute(text(f'SELECT COUNT(*) FROM "{nome}"')).scalar()
            print(f"    {nome}: {qtd} registros")

    print("\n[OK] Migracao concluida!")


if __name__ == "__main__":
    main()