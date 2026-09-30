import time
import tkinter as tk
from datetime import date, datetime, timedelta

import customtkinter as ctk
from customtkinter import CTkCanvas

from database.consultas import (
    criar_consulta,
    deletar_consulta,
    listar_consultas_com_paciente_por_data,
    listar_consultas_com_paciente_por_periodo,
    listar_tratamentos,
    proxima_consulta,
    update_consulta,
)
from database.orcamento import criar_orcamento, update_orcamento_por_consulta
from database.pacientes import buscar_paciente_por_nome

# ====================================================================================
# TELA: Agenda Semanal (estilo Google Agenda / Microsoft Teams)
# ------------------------------------------------------------------------------------
# Esquerda: mini-calendário mensal (clique no dia leva a semana + contagem regressiva
#           para a próxima consulta).
# Direita: grade semanal com 5 dias úteis, barra de horários e consultas como cards
#           posicionados proporcionalmente ao horário (granularidade 15/30/60 min).
# Dúvida: o DONO do relógio das abas possui a armação; nenhum card aqui é arrastável.
# ====================================================================================

DIA_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex"]
CABECALHO_CALENDARIO = ["D", "S", "T", "Q", "Q", "S", "S"]
MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

# Estado compartilhado entre os redesenhos da tela (sobrevive à troca de abas)
estado = {
    "data_selecionada": None,  # date — dia/log-âncora da semana exibida
    "mes_visivel": None,       # date — primeiro dia do mês mostrado no mini-calendário
    "granularidade": 30,       # 15 | 30 | 60 minutos
}

# Controle de dono do loop de atualização (evita loops antigos após troca de aba)
_dono_relogio = {"owner": 0}

GUTTER = 78          # largura da faixa com rótulos de horário
PX_HORA = 54         # altura mínima em pixels de 1 hora
HORA_INICIO = 7      # a grade começa às 07:00
HORA_FIM = 20        # e termina às 20:00
ALTURA_GRID = (HORA_FIM - HORA_INICIO) * PX_HORA
ALTURA_MIN_TRATAMENTO = 48  # abaixo disso o 2º label (tratamento) não cabe no card
RAIO_LINHA_AGORA = 5         # raio da bolinha no início da linha vermelha do "agora"
COR_COLUNA_HOJE = "#22314d"  # fundo da coluna do dia atual (usado atrás da bolinha)


def _altura_grid(canvas):
    """Altura do grid: estica para cobrir toda a altura disponível da tela."""
    return max(canvas.winfo_height(), ALTURA_GRID)

PALETA = ["#1a73e8", "#33b679", "#f4511e", "#8e24aa", "#039be5", "#e91e63", "#c0ca33", "#5f6368"]
COR_FUNDO = "#2b2d31"
COR_LINHA_HORA = "#4f545c"
COR_LINHA_SLOT = "#3a3d44"
COR_LINHA_DIA = "#45494f"
COR_HOJE = "#ea4335"
COR_ACCENT = "#1a73e8"
COR_HOVER = "#36383c"
COR_PAINEL = "#27292e"
COR_CARD_PROX = "#1f2126"
COR_BORDA_PAINEL = "#3a3d42"


def _inicializar_estado():
    if estado["data_selecionada"] is None:
        hoje = datetime.now().date()
        estado["data_selecionada"] = hoje
        estado["mes_visivel"] = date(hoje.year, hoje.month, 1)


def _inicio_semana(data):
    return data - timedelta(days=data.weekday())


def _conflita(inicio_a, fim_a, inicio_b, fim_b):
    """True se os intervalos [inicio_a, fim_a) e [inicio_b, fim_b) se sobrepõem.

    Limites exatos não conflitam: uma consulta pode terminar exatamente quando
    outra começa (fim == início é permitido).
    """
    return inicio_a < fim_b and inicio_b < fim_a


def _altura_card(px_hora, duracao):
    """Altura do card em pixels para uma duração: cobre [início, início+duração).

    Piso de 14px só para o card continuar clicável com durações minúsculas.
    """
    return max(px_hora * duracao / 60, 14)


def _consulta_passou(c, agora):
    """True se a consulta já terminou (fim = início + duração) em relação a `agora`."""
    fim = c["data"] + timedelta(minutes=(c.get("duracao") or 30))
    return fim <= agora


def _escurecer(cor):
    """Mistura a cor do card com o fundo da grade (consultas que já passaram)."""
    partes = (1, 3, 5)
    rgb_cor = tuple(int(cor[i : i + 2], 16) for i in partes)
    rgb_fundo = tuple(int(COR_FUNDO[i : i + 2], 16) for i in partes)
    return "#" + "".join(f"{round(c * 0.45 + f * 0.55):02x}" for c, f in zip(rgb_cor, rgb_fundo))


def mostrar(parent):
    """Constrói a tela da agenda semanal dentro do container pai."""
    _inicializar_estado()

    refs = {"canvas": None, "lab_dias": [], "titulo": None, "mini_container": None, "prox_container": None,
            "overlay_agora": None, "ponto_agora": None}
    itens_cards = {}  # consulta_id -> [item no canvas, widget do card] — reaproveita cards entre redraws
    cache_consultas = {"seg": None, "consultas": []}  # evita reconsultar o banco a cada redraw
    _cfg_redraw = {"pendente": None, "ult_tam": (0, 0)}  # debounce do evento <Configure>
    _mais = {"data": None, "hora": None, "ult": None, "abri_em": 0}  # botão "+" de hover

    seq = _dono_relogio["owner"] + 1
    _dono_relogio["owner"] = seq

    # ==================== CRIAR / EDITAR AGENDAMENTOS ====================

    def _achar_conflito(data_e_horario, duracao, ignorar_consulta_id=None):
        """Retorna a consulta que conflita com [início, início+duracao) no mesmo dia, ou None."""
        fim = data_e_horario + timedelta(minutes=duracao)
        try:
            consultas_dia = listar_consultas_com_paciente_por_data(data_e_horario.strftime("%Y-%m-%d"))
        except Exception:
            consultas_dia = []
        for c in consultas_dia:
            if c["consulta_id"] == ignorar_consulta_id:
                continue
            c_inicio = c["data"]
            c_fim = c_inicio + timedelta(minutes=(c.get("duracao") or 30))
            if _conflita(data_e_horario, fim, c_inicio, c_fim):
                return c
        return None

    def abrir_janela_novo_agendamento(data_selecionada, horario_selecionado):
        """Abre o pop-up de cadastro de um novo agendamento."""
        frame_criar_consulta = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        frame_criar_consulta.title("Novo Agendamento")

        largura_janela = 400

        paciente_selecionado = {"id": None, "nome": ""}

        def salvar_agendamento():
            tratamento = tratamento_dropdown.get()
            data_str = data_entry.get()
            horario_str = horario_entry.get()
            valor = valor_entry.get()
            metodo = metodo_dropdown.get()

            valor_str = valor.strip()
            if paciente_selecionado["id"] is None:
                resultado_salvar_label.configure(text="❌ Busque e selecione um paciente primeiro.", text_color="#f87171")
                return
            if tratamento not in tratamentos_lista:
                resultado_salvar_label.configure(text="❌ Selecione um tratamento.", text_color="#f87171")
                return
            if not valor_str:
                resultado_salvar_label.configure(text="❌ Digite um valor", text_color="#f87171")
                return

            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                horario_obj = datetime.strptime(horario_str, "%H:%M").time()
                data_e_horario_final = datetime.combine(data_obj.date(), horario_obj)
            except ValueError:
                resultado_salvar_label.configure(text="❌ Data ou Horário inválidos.", text_color="#ff4a4a")
                return

            duracao_texto = duracao_entry.get().strip()
            duracao = 30
            if duracao_texto:
                if not duracao_texto.isdigit() or int(duracao_texto) <= 0:
                    resultado_salvar_label.configure(text="❌ Duração inválida (minutos).", text_color="#ff4a4a")
                    return
                duracao = int(duracao_texto)

            conflito = _achar_conflito(data_e_horario_final, duracao)
            if conflito:
                resultado_salvar_label.configure(
                    text=f"❌ Conflito às {conflito['data'].strftime('%H:%M')}: {conflito['nome'].title()}",
                    text_color="#ff4a4a",
                )
                return

            try:
                consulta_id = criar_consulta(
                    paciente_selecionado["id"], tratamento, data_e_horario_final, valor, metodo, duracao=duracao
                )
                criar_orcamento(consulta_id, paciente_selecionado["id"], valor, metodo, data_e_horario_final, status=0)
            except Exception:
                resultado_salvar_label.configure(text="❌ Erro ao salvar no banco", text_color="#ff4a4a")
                return

            frame_criar_consulta.destroy()
            cache_consultas["seg"] = None
            renderizar()

        def buscar_paciente():
            nome = nome_busca_entry.get()
            if not nome.strip():
                resultado_label.configure(text="❌ Digite um nome para buscar.", text_color="#f87171")
                return

            try:
                pacientes = buscar_paciente_por_nome(nome)
            except Exception:
                resultado_label.configure(text="❌ Erro ao buscar paciente no banco", text_color="#f87171")
                return

            if len(pacientes) == 0:
                resultado_label.configure(text="❌ Paciente não encontrado", text_color="#f87171")
                paciente_selecionado["id"] = None
            elif len(pacientes) == 1:
                p = pacientes[0]
                paciente_selecionado["id"] = p.id
                paciente_selecionado["nome"] = p.nome
                resultado_label.configure(text=f"✓ {p.nome.title()}   CPF: {p.cpf}", text_color="#4ade80")
            else:
                resultado_label.configure(
                    text=f"⚠ {len(pacientes)} resultados. Seja mais específico.", text_color="#fbbf24"
                )

        ctk.CTkLabel(
            frame_criar_consulta, text="Criar Novo Agendamento", font=("Segoe UI", 16, "bold"), text_color="#ffffff"
        ).pack(pady=(15, 10))

        frame_formulario = ctk.CTkFrame(
            frame_criar_consulta, fg_color="#141517", border_width=1, border_color="#242528", corner_radius=10
        )
        frame_formulario.pack(fill="x", padx=25, pady=5)
        frame_formulario.columnconfigure(0, weight=1)
        frame_formulario.columnconfigure(1, weight=0)

        nome_busca_entry = ctk.CTkEntry(frame_formulario, placeholder_text="Nome do paciente", fg_color="#2b2b2b", height=35)
        nome_busca_entry.grid(row=0, column=0, sticky="ew", padx=(12, 6), pady=(12, 4))

        ctk.CTkButton(
            frame_formulario,
            text="Buscar",
            command=buscar_paciente,
            width=70,
            height=35,
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
        ).grid(row=0, column=1, sticky="e", padx=(0, 12), pady=(12, 4))

        resultado_label = ctk.CTkLabel(
            frame_formulario, text="🔍 Digite o nome e clique em Buscar", font=("Segoe UI", 11), text_color="#888888"
        )
        resultado_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(2, 12))

        try:
            tratamentos_db = listar_tratamentos()
        except Exception:
            tratamentos_db = []
        tratamentos_lista = [t.nome for t in tratamentos_db]

        def ao_selecionar_tratamento(tratamento_selecionado):
            valor = 0
            duracao_trat = None
            for t in tratamentos_db:
                if str(t.nome) == str(tratamento_selecionado):
                    valor = t.valor
                    duracao_trat = t.duracao
                    break
            valor_entry.delete(0, "end")
            valor_entry.insert(0, f"{float(valor):.2f}")
            duracao_entry.delete(0, "end")
            if duracao_trat is not None:
                duracao_entry.insert(0, str(duracao_trat))

        ctk.CTkLabel(frame_criar_consulta, text="Tratamento:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(
            anchor="w", padx=25, pady=(8, 0)
        )
        tratamento_dropdown = ctk.CTkComboBox(
            frame_criar_consulta,
            values=tratamentos_lista,
            width=350,
            fg_color="#2b2b2b",
            button_color="#3a3a3a",
            command=ao_selecionar_tratamento,
        )
        tratamento_dropdown.pack(pady=2)

        linha_data_hora = ctk.CTkFrame(frame_criar_consulta, fg_color="transparent")
        linha_data_hora.pack(fill="x", padx=25, pady=4)

        coluna_data = ctk.CTkFrame(linha_data_hora, fg_color="transparent")
        coluna_data.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkLabel(coluna_data, text="Data da Consulta:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(
            anchor="w"
        )
        data_entry = ctk.CTkEntry(coluna_data, placeholder_text="DD/MM/AAAA", fg_color="#2b2b2b")
        data_entry.pack(fill="x", pady=2)
        try:
            data_formatada = datetime.strptime(data_selecionada, "%Y-%m-%d").strftime("%d/%m/%Y")
            data_entry.insert(0, data_formatada)
        except ValueError:
            data_entry.insert(0, data_selecionada)

        coluna_hora = ctk.CTkFrame(linha_data_hora, fg_color="transparent")
        coluna_hora.pack(side="right", expand=True, fill="x", padx=(5, 0))
        ctk.CTkLabel(coluna_hora, text="Horário:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(anchor="w")
        horario_entry = ctk.CTkEntry(coluna_hora, placeholder_text="HH:MM", fg_color="#2b2b2b")
        horario_entry.pack(fill="x", pady=2)
        horario_entry.insert(0, horario_selecionado)

        linha_valor_pago = ctk.CTkFrame(frame_criar_consulta, fg_color="transparent")
        linha_valor_pago.pack(fill="x", padx=25, pady=4)

        coluna_valor = ctk.CTkFrame(linha_valor_pago, fg_color="transparent")
        coluna_valor.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkLabel(coluna_valor, text="Valor:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(anchor="w")
        valor_entry = ctk.CTkEntry(coluna_valor, placeholder_text="ex: 150.00", fg_color="#2b2b2b")
        valor_entry.pack(fill="x", pady=2)

        coluna_pagamento = ctk.CTkFrame(linha_valor_pago, fg_color="transparent")
        coluna_pagamento.pack(side="right", expand=True, fill="x", padx=(5, 0))
        ctk.CTkLabel(coluna_pagamento, text="Pagamento:", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(
            anchor="w"
        )
        metodo_dropdown = ctk.CTkComboBox(
            coluna_pagamento,
            values=["Pix", "Débito", "Crédito", "Dinheiro"],
            fg_color="#2b2b2b",
            button_color="#3a3a3a",
        )
        metodo_dropdown.pack(fill="x", pady=2)

        linha_duracao = ctk.CTkFrame(frame_criar_consulta, fg_color="transparent")
        linha_duracao.pack(fill="x", padx=25, pady=4)

        coluna_duracao = ctk.CTkFrame(linha_duracao, fg_color="transparent")
        coluna_duracao.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkLabel(coluna_duracao, text="Duração (min):", font=("Segoe UI", 11, "bold"), text_color="#a0a0a5").pack(
            anchor="w"
        )
        duracao_entry = ctk.CTkEntry(
            coluna_duracao, placeholder_text="em branco = 30 min", fg_color="#2b2b2b"
        )
        duracao_entry.pack(fill="x", pady=2)

        # Tratamento padrão: evita salvar o texto "CTkComboBox" quando nada é escolhido.
        # (fica aqui, depois dos campos, porque o autopreenchimento usa valor_entry e duracao_entry)
        if tratamentos_lista:
            tratamento_dropdown.set(tratamentos_lista[0])
            ao_selecionar_tratamento(tratamentos_lista[0])
        else:
            tratamento_dropdown.set("")

        resultado_salvar_label = ctk.CTkLabel(frame_criar_consulta, text="", font=("Segoe UI", 11))
        resultado_salvar_label.pack(pady=4)

        ctk.CTkButton(
            frame_criar_consulta,
            text="Confirmar Agendamento",
            command=salvar_agendamento,
            fg_color="#1f6aa5",
            hover_color="#144870",
            font=("Segoe UI", 13, "bold"),
            height=38,
            width=220,
        ).pack(pady=(5, 15))

        # Altura automática (o conteúdo pode variar) e centralização
        frame_criar_consulta.update_idletasks()
        altura_janela = frame_criar_consulta.winfo_reqheight()
        largura_tela = frame_criar_consulta.winfo_screenwidth()
        altura_tela = frame_criar_consulta.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))
        frame_criar_consulta.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        frame_criar_consulta.grab_set()

    def abrir_janela_editar(consulta):
        """Abre o pop-up de edição da consulta, com opção de excluir."""
        frame_editar_consulta = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        frame_editar_consulta.title("Editar Consulta")

        largura_janela = 400

        ctk.CTkLabel(
            frame_editar_consulta, text="Editar Agendamento", font=("Segoe UI", 16, "bold"), text_color="#ffffff"
        ).pack(pady=15)

        try:
            tratamentos_db = listar_tratamentos()
        except Exception:
            tratamentos_db = []
        tratamentos_lista = [t.nome for t in tratamentos_db]

        def ao_selecionar_tratamento(tratamento_selecionado):
            valor = 0
            duracao_trat = None
            for t in tratamentos_db:
                if str(t.nome) == str(tratamento_selecionado):
                    valor = t.valor
                    duracao_trat = t.duracao
                    break
            valor_entry.delete(0, "end")
            valor_entry.insert(0, f"{float(valor):.2f}")
            duracao_entry.delete(0, "end")
            if duracao_trat is not None:
                duracao_entry.insert(0, str(duracao_trat))

        tratamento_dropdown = ctk.CTkComboBox(
            frame_editar_consulta,
            values=tratamentos_lista,
            width=280,
            fg_color="#2b2b2b",
            button_color="#3a3a3a",
            command=ao_selecionar_tratamento,
        )
        tratamento_dropdown.pack(pady=6)
        tratamento_dropdown.set(consulta["tratamento"])

        data_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Data (DD/MM/AAAA)", fg_color="#2b2b2b")
        data_entry.pack(pady=6)
        data_entry.insert(0, consulta["data"].strftime("%d/%m/%Y"))

        horario_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Horário", fg_color="#2b2b2b")
        horario_entry.pack(pady=6)
        horario_entry.insert(0, consulta["data"].strftime("%H:%M"))

        valor_entry = ctk.CTkEntry(frame_editar_consulta, width=280, placeholder_text="Valor (ex: 150.00)", fg_color="#2b2b2b")
        valor_entry.pack(pady=6)
        valor_entry.insert(0, str(consulta["valor"]))

        metodo_dropdown = ctk.CTkComboBox(
            frame_editar_consulta,
            values=["Pix", "Débito", "Crédito", "Dinheiro", "Pendente"],
            width=280,
            fg_color="#2b2b2b",
            button_color="#3a3a3a",
        )
        metodo_dropdown.pack(pady=6)
        metodo_dropdown.set(consulta["metodo_pagamento"] if "metodo_pagamento" in consulta else "Método de pagamento")

        duracao_entry = ctk.CTkEntry(
            frame_editar_consulta, width=280, placeholder_text="Duração em minutos (30 padrão)", fg_color="#2b2b2b"
        )
        duracao_entry.pack(pady=6)
        duracao_entry.insert(0, str(consulta.get("duracao") or 30))

        resultado_editar_label = ctk.CTkLabel(frame_editar_consulta, text="", font=("Segoe UI", 12))
        resultado_editar_label.pack(pady=5)

        def realizar_update():
            novo_tratamento = tratamento_dropdown.get()
            data_str = data_entry.get()
            horario_str = horario_entry.get()
            novo_valor = valor_entry.get()
            novo_metodo = metodo_dropdown.get()

            valor_str = novo_valor.strip()
            if not valor_str:
                resultado_editar_label.configure(text="❌ Digite um valor.", text_color="#ff4a4a")
                return

            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                horario_obj = datetime.strptime(horario_str, "%H:%M").time()
                data_e_horario_final = datetime.combine(data_obj.date(), horario_obj)
            except ValueError:
                resultado_editar_label.configure(text="❌ Data ou Horário inválidos.", text_color="#ff4a4a")
                return

            duracao_texto = duracao_entry.get().strip()
            duracao = 30
            if duracao_texto:
                if not duracao_texto.isdigit() or int(duracao_texto) <= 0:
                    resultado_editar_label.configure(text="❌ Duração inválida (minutos).", text_color="#ff4a4a")
                    return
                duracao = int(duracao_texto)

            conflito = _achar_conflito(data_e_horario_final, duracao, ignorar_consulta_id=consulta["consulta_id"])
            if conflito:
                resultado_editar_label.configure(
                    text=f"❌ Conflito às {conflito['data'].strftime('%H:%M')}: {conflito['nome'].title()}",
                    text_color="#ff4a4a",
                )
                return

            try:
                update_consulta(
                    consulta["consulta_id"], novo_tratamento, data_e_horario_final, novo_valor, novo_metodo,
                    duracao=duracao,
                )
                update_orcamento_por_consulta(
                    consulta["consulta_id"], consulta["paciente_id"], novo_valor, novo_metodo, status=0
                )
            except Exception:
                resultado_editar_label.configure(text="❌ Erro ao atualizar no banco", text_color="#ff4a4a")
                return

            frame_editar_consulta.destroy()
            cache_consultas["seg"] = None
            renderizar()

        def excluir_consulta_seguro():
            try:
                deletar_consulta(consulta["consulta_id"])
            except Exception:
                pass
            frame_editar_consulta.destroy()
            cache_consultas["seg"] = None
            renderizar()

        linha_botoes = ctk.CTkFrame(frame_editar_consulta, fg_color="transparent")
        linha_botoes.pack(pady=15)

        ctk.CTkButton(
            linha_botoes,
            text="Salvar Alterações",
            command=realizar_update,
            fg_color="#1f6aa5",
            hover_color="#144870",
            font=("Segoe UI", 13, "bold"),
            height=35,
            width=170,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            linha_botoes,
            text="🗑 Excluir",
            command=excluir_consulta_seguro,
            fg_color="#361a1a",
            hover_color="#542323",
            text_color="#f87171",
            font=("Segoe UI", 13, "bold"),
            height=35,
            width=90,
        ).pack(side="left", padx=6)

        # Altura automática (o conteúdo pode variar) e centralização
        frame_editar_consulta.update_idletasks()
        altura_janela = frame_editar_consulta.winfo_reqheight()
        largura_tela = frame_editar_consulta.winfo_screenwidth()
        altura_tela = frame_editar_consulta.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))
        frame_editar_consulta.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        frame_editar_consulta.grab_set()

    # ==================== RENDERIZAÇÃO DA GRADE SEMANAL ====================

    def _pintar_card(card, cor_base, passou):
        """Aplica as cores do card: escurece a consulta que já terminou."""
        cor = _escurecer(cor_base) if passou else cor_base
        card.configure(fg_color=cor)
        card._lab_titulo.configure(bg=cor, fg="#8b9099" if passou else "#ffffff")
        card._lab_trat.configure(bg=cor, fg="#767b83" if passou else "#e8eaed")
        card._cor_base = cor_base
        card._cor_efetiva = cor
        card._passou = passou

    def criar_card_consulta(c, idx, passou=False):
        cor = PALETA[idx % len(PALETA)]
        hora = c["data"].strftime("%H:%M")
        card = ctk.CTkFrame(refs["canvas"], fg_color=cor, corner_radius=5)

        # tk.Label puro (fundo = cor do card): o CTkLabel desenha um canvas interno que
        # aparecia como uma faixa clara ("rebarba") sob o texto em cards baixos.
        lab_titulo = tk.Label(
            card, text=f"{hora}  {c['nome'].title()}", font=("Segoe UI", 14, "bold"),
            fg="#ffffff", bg=cor, bd=0, highlightthickness=0, padx=0, pady=0,
        )
        lab_titulo.pack(anchor="w", padx=7, pady=(2, 0))
        card._lab_titulo = lab_titulo

        # Label do tratamento: só aparece quando o card é alto o bastante (ver _ajustar_card)
        lab_trat = tk.Label(
            card, text=c["tratamento"], font=("Segoe UI", 9),
            fg="#e8eaed", bg=cor, bd=0, highlightthickness=0, padx=0, pady=0,
        )
        lab_trat.pack(anchor="w", padx=7, pady=(0, 3))
        card._lab_trat = lab_trat
        card._trat_visivel = True

        def ao_editar(e, cc=c):
            abrir_janela_editar(cc)

        card.bind("<Double-Button-1>", ao_editar)
        for filho in card.winfo_children():
            filho.bind("<Double-Button-1>", ao_editar)

        _pintar_card(card, cor, passou)
        return card

    def _cor_atras(cx, cy, x0, day_w, alt):
        """Cor que está atrás de um ponto (x, y) da grade: card, coluna de hoje ou fundo.

        A bolinha da linha do "agora" fica em cima de DUAS cores (metade na coluna de
        hoje, metade na coluna anterior), então ela é pintada com uma cor por metade —
        assim o widget quadrado fica invisível e sobra só o círculo.
        """
        canvas = refs["canvas"]
        for item in itens_cards.values():
            x, y = canvas.coords(item[0])
            larg = float(canvas.itemcget(item[0], "width"))
            altu = float(canvas.itemcget(item[0], "height"))
            if x <= cx <= x + larg and y <= cy <= y + altu:
                return item[1]._cor_efetiva
        if x0 <= cx <= x0 + day_w and 0 <= cy <= alt:
            return COR_COLUNA_HOJE
        return COR_FUNDO

    def _pintar_bolinha_agora(ponto, x_centro, y_centro, x0, day_w, alt):
        """Pinta o fundo da bolinha com a cor exata de cada metade (some com o quadrado)."""
        r = RAIO_LINHA_AGORA
        cor_esq = _cor_atras(x_centro - r / 2, y_centro, x0, day_w, alt)
        cor_dir = _cor_atras(x_centro + r / 2, y_centro, x0, day_w, alt)
        ponto.configure(bg=cor_esq)  # cor de segurança, caso o retângulo não cubra tudo
        ponto.delete("fundo_bolinha")
        ponto.create_rectangle(0, 0, r, 2 * r, fill=cor_esq, outline="", tags="fundo_bolinha")
        ponto.create_rectangle(r, 0, 2 * r, 2 * r, fill=cor_dir, outline="", tags="fundo_bolinha")
        ponto.tag_raise("bola")

    def _ajustar_card(card, altura):
        """Esconde o label de tratamento quando o card é baixo demais (evita a 'rebarba')."""
        mostrar_trat = altura >= ALTURA_MIN_TRATAMENTO
        if mostrar_trat == card._trat_visivel:
            return
        if mostrar_trat:
            card._lab_trat.pack(anchor="w", padx=7, pady=(0, 3))
        else:
            card._lab_trat.pack_forget()
        card._trat_visivel = mostrar_trat

    def desenhar_grade():
        canvas = refs["canvas"]
        canvas.delete("fundo")
        canvas.delete("linha_agora")
        canvas.delete("mais")
        _mais["ult"] = None

        cw = canvas.winfo_width()
        if cw < GUTTER + 60:
            cw = GUTTER + 900
        day_w = (cw - GUTTER) / 5

        seg = _inicio_semana(estado["data_selecionada"])
        dias = [seg + timedelta(days=i) for i in range(5)]
        gran = estado["granularidade"]
        minutos_visiveis = (HORA_FIM - HORA_INICIO) * 60
        alt = _altura_grid(canvas)
        px_hora = alt / (HORA_FIM - HORA_INICIO)

        # Hoje (para realçar a coluna do dia atual)
        agora = datetime.now()
        hoje = agora.date()
        if hoje in dias:
            xd = GUTTER + dias.index(hoje) * day_w
            canvas.create_rectangle(xd, 0, xd + day_w, alt, fill=COR_COLUNA_HOJE, outline="", tags="fundo")

        # Linhas horizontais (hora = forte, subdivisões = fracas)
        for minuto in range(HORA_INICIO * 60, HORA_FIM * 60, gran):
            y = (minuto - HORA_INICIO * 60) / minutos_visiveis * alt
            cor = COR_LINHA_HORA if minuto % 60 == 0 else COR_LINHA_SLOT
            canvas.create_line(GUTTER, y, cw, y, fill=cor, tags="fundo")

        # Rótulos de horário na faixa esquerda (nunca cortados na borda superior)
        for h in range(HORA_INICIO, HORA_FIM):
            y = max((h - HORA_INICIO) * px_hora, 8)
            canvas.create_text(
                GUTTER - 14, y, text=f"{h:02d}:00", fill="#c7ccd4",
                font=("Segoe UI", 12, "bold"), anchor="e", tags="fundo",
            )

        # Separadores verticais
        for i in range(6):
            x = GUTTER + i * day_w
            canvas.create_line(x, 0, x, alt, fill=COR_LINHA_DIA, tags="fundo")

        # Borda inferior (fecha a grade às 20:00)
        canvas.create_line(GUTTER, alt, cw, alt, fill=COR_LINHA_HORA, tags="fundo")
        canvas.tag_lower("fundo")  # fundo por baixo dos cards (que não são mais recriados)

        # Consultas da semana (uma query para os 5 dias, cacheada por semana)
        if cache_consultas["seg"] != seg:
            fim = seg + timedelta(days=6)
            try:
                cache_consultas["consultas"] = listar_consultas_com_paciente_por_periodo(seg, fim)
            except Exception:
                cache_consultas["consultas"] = []
            cache_consultas["seg"] = seg

        por_dia = {}
        for c in cache_consultas["consultas"]:
            por_dia.setdefault(c["data"].strftime("%Y-%m-%d"), []).append(c)

        presentes = set()
        idx = 0
        for i, d in enumerate(dias):
            for c in por_dia.get(d.strftime("%Y-%m-%d"), []):
                t = c["data"]
                duracao = c.get("duracao") or 30
                h_card = _altura_card(px_hora, duracao)
                min_inicio = t.hour * 60 + t.minute
                if min_inicio < HORA_INICIO * 60 or min_inicio >= HORA_FIM * 60:
                    continue
                x = GUTTER + i * day_w + 2
                y = (min_inicio - HORA_INICIO * 60) / minutos_visiveis * alt
                larg, altu = day_w - 4, h_card
                passou = _consulta_passou(c, agora)
                chave = c["consulta_id"]
                item = itens_cards.get(chave)
                if item is None:
                    card = criar_card_consulta(c, idx, passou)
                    novo_item = canvas.create_window(
                        x, y, anchor="nw", window=card, width=larg, height=altu, tags="cards"
                    )
                    itens_cards[chave] = [novo_item, card]
                    _ajustar_card(card, altu)
                else:
                    canvas.coords(item[0], x, y)
                    canvas.itemconfigure(item[0], width=larg, height=altu)
                    _ajustar_card(item[1], altu)
                    # Repinta quando a consulta termina enquanto a tela está aberta
                    if item[1]._passou != passou:
                        _pintar_card(item[1], item[1]._cor_base, passou)
                presentes.add(chave)
                idx += 1

        # Remove cards de consultas que saíram da semana exibida
        for chave in [k for k in itens_cards if k not in presentes]:
            item, card = itens_cards.pop(chave)
            canvas.delete(item)
            card.destroy()

        # Linha vermelha do momento atual.
        # BARRA e BOLINHA são widgets sobrepostos ao canvas: os cards são janelas
        # embutidas (create_window) e ficariam por cima de qualquer item do canvas.
        # Como widget é retângulo, a bolinha veste a cor que está atrás dela
        # (ver _cor_atras_da_bolinha) para os cantos não aparecerem.
        barra = refs["overlay_agora"]
        ponto = refs["ponto_agora"]
        if hoje in dias and HORA_INICIO * 60 <= agora.hour * 60 + agora.minute < HORA_FIM * 60:
            x0 = GUTTER + dias.index(hoje) * day_w
            ym = (agora.hour * 60 + agora.minute - HORA_INICIO * 60) / minutos_visiveis * alt
            r = RAIO_LINHA_AGORA
            x_ponto = x0 - r  # bolinha centrada na borda esquerda da coluna de hoje
            y_vis = ym - canvas.canvasy(0)  # desconta o scroll vertical da grade
            barra.place(x=x0, y=y_vis - 1, width=max(day_w, 1), height=2)
            ponto.place(x=x_ponto, y=y_vis - r, width=2 * r, height=2 * r)
            _pintar_bolinha_agora(ponto, x0, ym, x0, day_w, alt)
            barra.tkraise()
            # tk.Canvas remapeia lift()/tkraise() para "raise de item", então o comando
            # Tcl é chamado direto para subir o widget na pilha.
            ponto.tk.call("raise", ponto._w)
        else:
            barra.place_forget()
            ponto.place_forget()

        canvas.configure(scrollregion=(0, 0, max(cw, GUTTER + 5 * day_w), alt))

    def _redesenhos_agendado():
        _cfg_redraw["pendente"] = None
        canvas = refs["canvas"]
        if not canvas.winfo_exists():
            return
        _cfg_redraw["ult_tam"] = (canvas.winfo_width(), canvas.winfo_height())
        desenhar_grade()

    def _ao_configure(e):
        canvas = refs["canvas"]
        dim = (canvas.winfo_width(), canvas.winfo_height())
        if not dim[0] or not dim[1] or dim == _cfg_redraw["ult_tam"] or _cfg_redraw["pendente"] is not None:
            return
        _cfg_redraw["pendente"] = parent.after(40, _redesenhos_agendado)

    def _limpar_mais():
        if "canvas" in refs:
            refs["canvas"].delete("mais")
        _mais["ult"] = None

    def _clicar_mais():
        if _mais["data"]:
            abrir_janela_novo_agendamento(_mais["data"], _mais["hora"])
            _mais["abri_em"] = time.time()
            _limpar_mais()

    def _ao_mover_mouse(e):
        canvas = refs["canvas"]
        cx = canvas.canvasx(e.x)
        cy = canvas.canvasy(e.y)
        cw = canvas.winfo_width()
        if cw < GUTTER + 60:
            _limpar_mais()
            return
        day_w2 = (cw - GUTTER) / 5
        col = int((cx - GUTTER) // day_w2)
        if cx < GUTTER or cx > GUTTER + 5 * day_w2 or not 0 <= col <= 4:
            _limpar_mais()
            return

        gran = estado["granularidade"]
        minutos_visiveis = (HORA_FIM - HORA_INICIO) * 60
        alt = _altura_grid(canvas)
        min_rel = int(cy / alt * minutos_visiveis)
        min_rel = min(min_rel, minutos_visiveis - gran)
        total = HORA_INICIO * 60 + min_rel // gran * gran

        sobre_card = any(
            "cards" in canvas.gettags(i)
            for i in canvas.find_overlapping(cx, cy, cx, cy)
        )
        if sobre_card:
            _limpar_mais()
            return

        if _mais["ult"] == (col, total):
            return

        seg = _inicio_semana(estado["data_selecionada"])
        data = seg + timedelta(days=col)
        hh, mm = divmod(total, 60)
        _mais["data"] = data.strftime("%Y-%m-%d")
        _mais["hora"] = f"{hh:02d}:{mm:02d}"
        _mais["ult"] = (col, total)

        canvas.delete("mais")
        slot_h = alt / minutos_visiveis * gran
        x_centro = GUTTER + col * day_w2 + day_w2 / 2
        y_topo = (total - HORA_INICIO * 60) / minutos_visiveis * alt
        y_centro = y_topo + slot_h / 2
        r = min(18, max(11, int(slot_h / 2) - 3))
        # Área de clique invisível + "+" cinza claro e discreto (sem fundo)
        canvas.create_oval(x_centro - r, y_centro - r, x_centro + r, y_centro + r, fill="", outline="", tags="mais")
        canvas.create_text(x_centro, y_centro, text="＋", fill="#9aa0a6", font=("Segoe UI", 18, "bold"), tags="mais")
        canvas.tag_raise("mais")

    def _ao_clique(e):
        if time.time() - _mais.get("abri_em", 0) < 0.6:
            return
        canvas = refs["canvas"]
        cx = canvas.canvasx(e.x)
        cy = canvas.canvasy(e.y)
        if any("mais" in canvas.gettags(i) for i in canvas.find_overlapping(cx, cy, cx, cy)):
            _clicar_mais()
        else:
            _limpar_mais()

    def ao_duplo_clique(e):
        """Duplo clique em área vazia abre 'novo agendamento' naquele dia/horário."""
        canvas = refs["canvas"]
        if time.time() - _mais.get("abri_em", 0) < 0.6:
            return
        x = canvas.canvasx(e.x)
        y = canvas.canvasy(e.y)
        cw = canvas.winfo_width()
        if cw < GUTTER + 60:
            return
        day_w = (cw - GUTTER) / 5
        alt = _altura_grid(canvas)
        if x < GUTTER or x > GUTTER + 5 * day_w:
            return
        col = int((x - GUTTER) // day_w)
        if not 0 <= col <= 4:
            return

        gran = estado["granularidade"]
        minutos_visiveis = (HORA_FIM - HORA_INICIO) * 60
        min_rel = int(y / alt * minutos_visiveis)
        min_rel = min(min_rel, minutos_visiveis - gran)
        total = HORA_INICIO * 60 + min_rel // gran * gran

        seg = _inicio_semana(estado["data_selecionada"])
        data = seg + timedelta(days=col)
        hh, mm = divmod(total, 60)
        abrir_janela_novo_agendamento(data.strftime("%Y-%m-%d"), f"{hh:02d}:{mm:02d}")

    def criar_no_dia(idx, hora="08:00"):
        seg = _inicio_semana(estado["data_selecionada"])
        data = seg + timedelta(days=idx)
        abrir_janela_novo_agendamento(data.strftime("%Y-%m-%d"), hora)

    # ==================== MINI-CALENDÁRIO MENSAL ====================

    def renderizar_mini_calendario():
        ct = refs["mini_container"]
        for w in ct.winfo_children():
            w.destroy()

        m = estado["mes_visivel"]  # date do 1º dia do mês

        topo = ctk.CTkFrame(ct, fg_color="transparent")
        topo.pack(fill="x", padx=4, pady=(6, 2))

        ctk.CTkButton(
            topo, text="‹", width=26, height=24, corner_radius=6, fg_color="transparent",
            hover_color=COR_HOVER, text_color="#dadce0", font=("Segoe UI", 15, "bold"),
            command=lambda: _mover_mes(-1),
        ).pack(side="left")

        ctk.CTkLabel(
            topo, text=f"{MESES[m.month - 1]} {m.year}", font=("Segoe UI", 12, "bold"), text_color="#e8eaed"
        ).pack(side="left", expand=True)

        ctk.CTkButton(
            topo, text="›", width=26, height=24, corner_radius=6, fg_color="transparent",
            hover_color=COR_HOVER, text_color="#dadce0", font=("Segoe UI", 15, "bold"),
            command=lambda: _mover_mes(1),
        ).pack(side="left")

        grade = ctk.CTkFrame(ct, fg_color="transparent")
        grade.pack(fill="x", padx=4, pady=(0, 6))

        for col, nome in enumerate(CABECALHO_CALENDARIO):
            ctk.CTkLabel(grade, text=nome, width=30, height=20, font=("Segoe UI", 9), text_color="#8f959e").grid(
                row=0, column=col, padx=1
            )

        primeiro = date(m.year, m.month, 1)
        desloc = primeiro.weekday()  # 0 = segunda
        hoje = datetime.now().date()
        sel = estado["data_selecionada"]

        for d in range(1, 32):
            try:
                dt = date(m.year, m.month, d)
            except ValueError:
                break
            coluna = (desloc + d - 1) % 7
            linha = 1 + (desloc + d - 1) // 7

            if dt == hoje:
                fg_, tx = COR_ACCENT, "#ffffff"
            elif dt == sel:
                fg_, tx = "#3b4a63", "#e8eaed"
            else:
                fg_, tx = "transparent", "#c6cbd1"

            ctk.CTkButton(
                grade, text=str(d), width=30, height=24, corner_radius=6, fg_color=fg_, hover_color=COR_HOVER,
                text_color=tx, font=("Segoe UI", 10, "bold"), command=lambda dd=d: _escolher_dia(dd),
            ).grid(row=linha, column=coluna, padx=1, pady=1)

    # ==================== PRÓXIMA CONSULTA (COUNTDOWN) ====================

    def atualizar_proxima():
        ct = refs["prox_container"]
        if not ct.winfo_exists():
            return
        for w in ct.winfo_children():
            w.destroy()

        try:
            p = proxima_consulta(datetime.now())
        except Exception:
            p = None

        if not p:
            ctk.CTkLabel(ct, text="Nenhuma consulta futura", font=("Segoe UI", 11), text_color="#9aa0a6").pack(
                padx=12, pady=16
            )
            return

        segs = int((p["data"] - datetime.now()).total_seconds())
        if segs <= 0:
            texto = "acontecendo agora"
        else:
            dias, r = divmod(segs, 86400)
            horas, r = divmod(r, 3600)
            minutos, _ = divmod(r, 60)
            partes = []
            if dias:
                partes.append(f"{dias}d")
            if horas:
                partes.append(f"{horas}h")
            partes.append(f"{minutos}min")
            texto = "em " + " ".join(partes)

        ctk.CTkLabel(ct, text=texto, font=("Segoe UI", 20, "bold"), text_color="#8ab4f8").pack(padx=12, pady=(12, 2))
        ctk.CTkLabel(ct, text=p["nome"].title(), font=("Segoe UI", 13, "bold"), text_color="#e8eaed").pack(padx=12)
        ctk.CTkLabel(
            ct, text=f"{p['tratamento']}  •  {p['data'].strftime('%d/%m  %H:%M')}",
            font=("Segoe UI", 10), text_color="#9aa0a6",
        ).pack(padx=12, pady=(0, 12))

    def loop_proxima():
        if not parent.winfo_exists() or _dono_relogio["owner"] != seq:
            return
        atualizar_proxima()
        parent.after(30000, loop_proxima)

    # ==================== NAVEGAÇÃO ====================

    def _escolher_dia(d):
        m = estado["mes_visivel"]
        dt = date(m.year, m.month, d)
        estado["data_selecionada"] = dt
        renderizar()

    def _mover_mes(delta):
        m = estado["mes_visivel"]
        novo_mes = (m.month - 1 + delta) % 12 + 1
        novo_ano = m.year + (m.month - 1 + delta) // 12
        estado["mes_visivel"] = date(novo_ano, novo_mes, 1)
        renderizar()

    def mover_semana(delta):
        estado["data_selecionada"] += timedelta(days=7 * delta)
        seg = _inicio_semana(estado["data_selecionada"])
        estado["mes_visivel"] = date(seg.year, seg.month, 1)
        renderizar()

    def ir_hoje():
        hoje = datetime.now().date()
        estado["data_selecionada"] = hoje
        estado["mes_visivel"] = date(hoje.year, hoje.month, 1)
        renderizar()

    def _mudar_granularidade(valor):
        estado["granularidade"] = int(valor.split()[0])
        desenhar_grade()

    def renderizar():
        seg = _inicio_semana(estado["data_selecionada"])
        dias = [seg + timedelta(days=i) for i in range(5)]
        hoje = datetime.now().date()

        for i, d in enumerate(dias):
            num = refs["lab_dias"][i]
            num.configure(text=str(d.day))
            if d == hoje:
                num.configure(fg_color=COR_ACCENT, text_color="#ffffff")
            else:
                num.configure(fg_color="transparent", text_color="#e8eaed")

        renderizar_mini_calendario()
        desenhar_grade()
        atualizar_proxima()

    # ==================== CONSTRUÇÃO DA TELA ====================

    barra = ctk.CTkFrame(parent, fg_color="transparent")
    barra.pack(fill="x", padx=6, pady=(6, 12))

    def _botao_barra(texto, comando, largura=90):
        return ctk.CTkButton(
            barra, text=texto, width=largura, height=36, corner_radius=10,
            font=("Segoe UI", 13, "bold"), fg_color="#2b2d31", hover_color="#3a3d42",
            text_color="#e8eaed", command=comando,
        )

    _botao_barra("◀ Anterior", lambda: mover_semana(-1)).pack(side="left", padx=(0, 4))
    _botao_barra("Hoje", ir_hoje).pack(side="left", padx=4)
    _botao_barra("Próxima ▶", lambda: mover_semana(1)).pack(side="left", padx=(4, 0))

    gran_seg = ctk.CTkSegmentedButton(
        barra, values=["15 min", "30 min", "60 min"], command=_mudar_granularidade, height=36,
        font=("Segoe UI", 12, "bold"), selected_color=COR_ACCENT, selected_hover_color="#1765cc",
        unselected_color="#2b2d31", unselected_hover_color="#3a3d42", text_color="#e8eaed",
        fg_color="#2b2d31",
    )
    gran_seg.pack(side="right")
    gran_seg.set(f"{estado['granularidade']} min")

    dica = ctk.CTkLabel(
        parent, text="Dica: duplo clique num horário vazio para agendar • duplo clique num card edita",
        font=("Segoe UI", 11), text_color="#9aa0a6",
    )
    dica.pack(anchor="w", padx=10, pady=(0, 6))

    split = ctk.CTkFrame(parent, fg_color="transparent")
    split.pack(fill="both", expand=True)
    split.grid_columnconfigure(1, weight=1)
    split.rowconfigure(0, weight=1)

    # ---- painel esquerdo (mini-calendário + próxima consulta) ----
    painel_esq = ctk.CTkFrame(
        split, width=295, corner_radius=10, fg_color=COR_PAINEL, border_width=1, border_color=COR_BORDA_PAINEL
    )
    painel_esq.grid(row=0, column=0, sticky="ns", padx=(2, 10))
    painel_esq.grid_propagate(False)

    ctk.CTkLabel(
        painel_esq, text="📅 Calendário", font=("Segoe UI", 13, "bold"), text_color="#e8eaed"
    ).pack(anchor="w", padx=12, pady=(12, 4))

    mini_container = ctk.CTkFrame(painel_esq, fg_color="transparent")
    mini_container.pack(fill="x", padx=6, pady=(0, 4))
    refs["mini_container"] = mini_container

    ctk.CTkLabel(
        painel_esq, text="⏱ Próxima consulta", font=("Segoe UI", 13, "bold"), text_color="#e8eaed"
    ).pack(anchor="w", padx=12, pady=(16, 4))

    prox_container = ctk.CTkFrame(
        painel_esq, fg_color=COR_CARD_PROX, corner_radius=10, border_width=1, border_color=COR_BORDA_PAINEL
    )
    prox_container.pack(fill="x", padx=12, pady=(0, 12))
    refs["prox_container"] = prox_container

    # ---- painel direito (grade semanal) ----
    painel_dir = ctk.CTkFrame(split, fg_color="transparent")
    painel_dir.grid(row=0, column=1, sticky="nsew")

    cabecalho = ctk.CTkFrame(painel_dir, fg_color="transparent")
    cabecalho.pack(fill="x", pady=(0, 4))
    cabecalho.grid_columnconfigure(0, minsize=GUTTER)
    for i in range(5):
        cabecalho.grid_columnconfigure(i + 1, weight=1, uniform="dia")

    def _celula_dia(i):
        celula = ctk.CTkFrame(cabecalho, fg_color="transparent")
        celula.grid(row=0, column=i + 1)

        ctk.CTkLabel(celula, text=DIA_SEMANA[i], font=("Segoe UI", 11), text_color="#9aa0a6").pack(
            side="left", padx=(0, 6)
        )
        num = ctk.CTkLabel(
            celula, text="", font=("Segoe UI", 13, "bold"), text_color="#e8eaed",
            corner_radius=14, width=28, height=28,
        )
        num.pack(side="left")

        ctk.CTkButton(
            celula, text="＋", width=28, height=28, corner_radius=8, fg_color="transparent",
            hover_color=COR_HOVER, text_color="#9aa0a6", font=("Segoe UI", 14, "bold"),
            command=lambda idx=i: criar_no_dia(idx),
        ).pack(side="right", padx=(10, 0))
        return num

    refs["lab_dias"] = [_celula_dia(i) for i in range(5)]

    corpo = ctk.CTkFrame(painel_dir, fg_color="transparent")
    corpo.pack(fill="both", expand=True)

    canvas = CTkCanvas(corpo, bg=COR_FUNDO, highlightthickness=0, bd=0)
    scrollbar = ctk.CTkScrollbar(corpo, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    refs["canvas"] = canvas

    canvas.bind("<Configure>", _ao_configure)
    canvas.bind("<Double-Button-1>", ao_duplo_clique)
    canvas.bind("<Motion>", _ao_mover_mouse)
    canvas.bind("<Leave>", lambda e: _limpar_mais())
    canvas.bind("<Button-1>", _ao_clique)

    # Barra e bolinha do "agora" como widgets IRMÃOS do canvas (mesma origem => e.x/e.y
    # batem com o canvas, então os mesmos handlers funcionam). Criados depois do canvas
    # para ficarem acima dele na pilha de widgets.
    # IMPORTANTE: tk puro e não CTk, porque CTkBaseClass.place() multiplica x/y pelo
    # scaling da tela e a linha saía deslocada.
    r_agora = RAIO_LINHA_AGORA
    barra_agora = tk.Frame(corpo, bg=COR_HOJE, height=2, highlightthickness=0, bd=0)
    ponto_agora = tk.Canvas(
        corpo, width=2 * r_agora, height=2 * r_agora, bg=COR_COLUNA_HOJE,
        highlightthickness=0, bd=0,
    )
    ponto_agora.create_oval(0, 0, 2 * r_agora, 2 * r_agora, fill=COR_HOJE, outline="", tags="bola")
    refs["overlay_agora"] = barra_agora
    refs["ponto_agora"] = ponto_agora
    for w in (barra_agora, ponto_agora):
        w.bind("<Double-Button-1>", ao_duplo_clique)
        w.bind("<Motion>", _ao_mover_mouse)
        w.bind("<Leave>", lambda e: _limpar_mais())
        w.bind("<Button-1>", _ao_clique)

    renderizar()
    loop_proxima()