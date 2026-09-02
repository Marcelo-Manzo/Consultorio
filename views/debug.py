import os
import platform
import sys
from datetime import datetime

import customtkinter as ctk
from sqlalchemy import text

from database.connection import DATABASE_URL, get_db


def mostrar(parent):
    log_entries = []

    def log(msg, nivel="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        cores = {"INFO": "#60a5fa", "OK": "#4ade80", "ERRO": "#f87171", "AVISO": "#fbbf24"}
        cor = cores.get(nivel, "#9ca3af")
        log_entries.append({"hora": timestamp, "msg": msg, "cor": cor})
        renderizar_log()

    def renderizar_log():
        for widget in frame_log.winfo_children():
            widget.destroy()
        for entry in log_entries[-50:]:
            ctk.CTkLabel(
                frame_log,
                text=f"[{entry['hora']}] {entry['msg']}",
                font=("Consolas", 11),
                text_color=entry["cor"],
                anchor="w",
            ).pack(anchor="w", padx=5, pady=1)
        frame_log._parent_canvas.yview_moveto(1.0)

    def testar_conexao():
        lbl_status_db.configure(text="Testando...", text_color="#fbbf24")
        parent.update_idletasks()

        try:
            with get_db() as db:
                result = db.execute(text("SELECT 1"))
                result.fetchone()
            lbl_status_db.configure(text="Conectado", text_color="#4ade80")
            log("Conexão com o banco de dados OK", "OK")
        except Exception as e:
            lbl_status_db.configure(text="Erro de conexão", text_color="#f87171")
            log(f"Falha na conexão: {e}", "ERRO")

    def contar_registros():
        lbl_status_db.configure(text="Consultando...", text_color="#fbbf24")
        parent.update_idletasks()

        tabelas = {
            "Pacientes": "SELECT COUNT(*) FROM Pacientes",
            "Consultas": "SELECT COUNT(*) FROM Consultas",
            "Orcamentos": "SELECT COUNT(*) FROM Orcamentos",
            "Tratamentos": "SELECT COUNT(*) FROM Tratamentos",
        }

        try:
            with get_db() as db:
                for nome, query in tabelas.items():
                    result = db.execute(text(query))
                    count = result.scalar()
                    card = cards_tabelas[nome]
                    card["qtd"].configure(text=str(count))
                    log(f"{nome}: {count} registros", "INFO")

            lbl_status_db.configure(text="Consulta concluída", text_color="#4ade80")
        except Exception as e:
            lbl_status_db.configure(text="Erro ao consultar", text_color="#f87171")
            log(f"Erro ao contar registros: {e}", "ERRO")

    def rodar_diagnostico_completo():
        log("=== INICIANDO DIAGNÓSTICO ===", "INFO")

        log(f"Sistema: {platform.system()} {platform.release()}", "INFO")
        log(f"Python: {sys.version.split()[0]}", "INFO")
        log(f"Arquitetura: {platform.machine()}", "INFO")
        log(f"Diretório: {os.getcwd()}", "INFO")

        db_host = DATABASE_URL.split("@")[-1].split("/")[0] if DATABASE_URL and "@" in DATABASE_URL else "N/A"
        log(f"Banco de dados: {db_host}", "INFO")

        testar_conexao()
        contar_registros()

        log("=== DIAGNÓSTICO CONCLUÍDO ===", "OK")

    def limpar_log():
        log_entries.clear()
        renderizar_log()

    # ==================== LAYOUT ====================

    # Título
    ctk.CTkLabel(parent, text="Debug & Diagnóstico", font=("Segoe UI", 24, "bold"), text_color="#ffffff").pack(
        anchor="w", padx=25, pady=(20, 10)
    )

    # Container principal dividido em 2 colunas
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=25, pady=(0, 20))
    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(1, weight=1)

    # ==================== COLUNA ESQUERDA ====================

    # Card: Status do Banco
    frame_db = ctk.CTkFrame(container, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
    frame_db.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))

    ctk.CTkLabel(frame_db, text="Banco de Dados", font=("Segoe UI", 14, "bold"), text_color="#ffffff").pack(
        anchor="w", padx=15, pady=(12, 5)
    )

    frame_status = ctk.CTkFrame(frame_db, fg_color="transparent")
    frame_status.pack(fill="x", padx=15, pady=5)

    ctk.CTkLabel(frame_status, text="Status:", font=("Segoe UI", 12), text_color="#9ca3af").pack(side="left")
    lbl_status_db = ctk.CTkLabel(frame_status, text="Não testado", font=("Segoe UI", 12, "bold"), text_color="#fbbf24")
    lbl_status_db.pack(side="left", padx=5)

    frame_botoes_db = ctk.CTkFrame(frame_db, fg_color="transparent")
    frame_botoes_db.pack(fill="x", padx=15, pady=(5, 12))

    ctk.CTkButton(
        frame_botoes_db,
        text="Testar Conexão",
        command=testar_conexao,
        fg_color="#1f6aa5",
        hover_color="#144870",
        font=("Segoe UI", 11, "bold"),
        height=30,
    ).pack(side="left", padx=(0, 5))

    ctk.CTkButton(
        frame_botoes_db,
        text="Contar Registros",
        command=contar_registros,
        fg_color="#2b2b2b",
        hover_color="#3a3a3a",
        font=("Segoe UI", 11, "bold"),
        height=30,
    ).pack(side="left")

    # Cards de contagem
    frame_cards = ctk.CTkFrame(container, fg_color="transparent")
    frame_cards.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
    frame_cards.columnconfigure((0, 1), weight=1)

    cards_tabelas = {}
    nomes_tabelas = [("Pacientes", 0, 0), ("Consultas", 0, 1), ("Orcamentos", 1, 0), ("Tratamentos", 1, 1)]

    for nome, row, col in nomes_tabelas:
        card = ctk.CTkFrame(frame_cards, fg_color="#1e1f22", border_width=1, border_color="#2b2d31", corner_radius=8)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        ctk.CTkLabel(card, text=nome, font=("Segoe UI", 11, "bold"), text_color="#949ba4").pack(anchor="w", padx=12, pady=(8, 2))

        lbl_qtd = ctk.CTkLabel(card, text="--", font=("Segoe UI", 20, "bold"), text_color="#ffffff")
        lbl_qtd.pack(anchor="w", padx=12, pady=(0, 8))

        cards_tabelas[nome] = {"qtd": lbl_qtd}

    # Botão diagnóstico completo
    ctk.CTkButton(
        container,
        text="Rodar Diagnóstico Completo",
        command=rodar_diagnostico_completo,
        fg_color="#2b7a3e",
        hover_color="#1e542b",
        font=("Segoe UI", 13, "bold"),
        height=38,
    ).grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

    # ==================== COLUNA DIREITA (LOG) ====================

    frame_log_container = ctk.CTkFrame(container, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10)
    frame_log_container.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=(8, 0), pady=(0, 10))

    header_log = ctk.CTkFrame(frame_log_container, fg_color="transparent")
    header_log.pack(fill="x", padx=12, pady=(10, 5))

    ctk.CTkLabel(header_log, text="Log do Sistema", font=("Segoe UI", 14, "bold"), text_color="#ffffff").pack(
        side="left"
    )

    ctk.CTkButton(
        header_log,
        text="Limpar",
        command=limpar_log,
        fg_color="#361a1a",
        hover_color="#542323",
        text_color="#f87171",
        font=("Segoe UI", 10, "bold"),
        width=60,
        height=26,
    ).pack(side="right")

    ctk.CTkFrame(frame_log_container, fg_color="#242528", height=1).pack(fill="x", padx=12, pady=(0, 5))

    frame_log = ctk.CTkScrollableFrame(frame_log_container, fg_color="transparent", label_text="")
    frame_log.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    # Log inicial
    log("Sistema iniciado", "OK")
    log(f"Plataforma: {platform.system()} {platform.release()}", "INFO")
    log(f"Python: {sys.version.split()[0]}", "INFO")
