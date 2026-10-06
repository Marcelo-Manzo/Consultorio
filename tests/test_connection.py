"""Testes do database/connection.py (nao tocam no Supabase: tudo é stub)."""

from database.connection import _adaptar_url, _anular_commit_spurio


class _ConexaoFalsa:
    """Substitui a conexão do pg8000 só para observar o que é chamado."""

    def __init__(self, autocommit):
        self.autocommit = autocommit
        self.commits = 0

    def commit(self):
        self.commits += 1


class TestAdaptarUrl:
    def test_troca_psycopg2_por_pg8000(self):
        url = "postgresql+psycopg2://u:senha@host:5432/banco"
        assert _adaptar_url(url) == "postgresql+pg8000://u:senha@host:5432/banco"

    def test_aceita_atalhos_do_supabase(self):
        for url in (
            "postgres://u:senha@host:5432/banco",
            "postgresql://u:senha@host:5432/banco",
        ):
            assert _adaptar_url(url) == "postgresql+pg8000://u:senha@host:5432/banco"

    def test_pg8000_ja_fica_igual(self):
        url = "postgresql+pg8000://u:senha@host:5432/banco"
        assert _adaptar_url(url) == url

    def test_nao_mexe_em_outros_drivers(self):
        url = "mssql+pyodbc://u:senha@host/banco"
        assert _adaptar_url(url) == url


class TestAnularCommitSpurio:
    """O COMMIT sem transação que o Postgresrespondia com WARNING.

    Em AUTOCOMMIT o statement já foi confirmado pelo servidor, então o commit
    do driver é inócuo e só polui o log do Supabase.
    """

    def test_anula_commit_em_autocommit(self):
        conexao = _ConexaoFalsa(autocommit=True)
        _anular_commit_spurio(conexao, None)
        conexao.commit()
        assert conexao.commits == 0

    def test_preserva_commit_em_transacao_explicita(self):
        conexao = _ConexaoFalsa(autocommit=False)
        _anular_commit_spurio(conexao, None)
        conexao.commit()
        assert conexao.commits == 1

    def test_driver_sem_autocommit_nao_quebra(self):
        class SemAtributo:
            def commit(self):
                return "commit real"

        conexao = SemAtributo()
        _anular_commit_spurio(conexao, None)
        assert conexao.commit() == "commit real"
