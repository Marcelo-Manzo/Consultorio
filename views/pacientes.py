import re
import customtkinter as ctk
from database.models import (
    buscar_paciente_por_cpf,
    buscar_paciente_por_nome,
    criar_paciente,
    atualizar_paciente,  # <--- Certifique-se de importar a função de atualizar
    listar_pacientes,
    excluir_paciente_por_id,
    listar_consultas_paciente,
)
from validate_docbr import CPF


def mostrar(parent):
    def abrir_modal_historico(paciente):
        popup = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        popup.title(f"Histórico - {paciente.nome}")

        # 1. Centralização da janela no topo
        largura_janela, altura_janela = 460, 480
        largura_tela = popup.winfo_screenwidth()
        altura_tela = popup.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        popup.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        popup.grab_set()

        # 2. Cabeçalho estilizado
        frame_header = ctk.CTkFrame(popup, fg_color="transparent")
        frame_header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            frame_header, 
            text=f"📋 {paciente.nome}", 
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame_header, 
            text=f"CPF: {paciente.cpf}  •  {paciente.telefone}", 
            font=("Segoe UI", 11),
            text_color="#9ca3af"
        ).pack(anchor="w", pady=(2, 0))

        # Divisor visual
        ctk.CTkFrame(popup, height=1, fg_color="#2e2f33").pack(fill="x", padx=20, pady=10)

        # 3. Container rolável
        container_consultas = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        container_consultas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        consultas = listar_consultas_paciente(paciente.id)

        # 4. Estado vazio (sem consultas)
        if not consultas:
            ctk.CTkLabel(
                container_consultas,
                text="Nenhuma consulta registrada para este paciente.",
                font=("Segoe UI", 12, "italic"),
                text_color="#6b7280"
            ).pack(pady=40)
            return

        # 5. Lista de cards estilizados
        for c in consultas:
            card_historico = ctk.CTkFrame(
                container_consultas, 
                fg_color="#25262b", 
                border_width=1, 
                border_color="#333438", 
                corner_radius=8
            )
            card_historico.pack(fill="x", padx=5, pady=4)

            # Lado Esquerdo: Detalhes do Procedimento e Data
            frame_info = ctk.CTkFrame(card_historico, fg_color="transparent")
            frame_info.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            ctk.CTkLabel(
                frame_info,
                text=c.tratamento,
                font=("Segoe UI", 13, "bold"),
                text_color="#e5e7eb"
            ).pack(anchor="w")

            data_formatada = c.data.strftime('%d/%m/%Y às %H:%M')
            ctk.CTkLabel(
                frame_info,
                text=f"📅 {data_formatada}",
                font=("Segoe UI", 11),
                text_color="#9ca3af"
            ).pack(anchor="w", pady=(2, 0))

            # Lado Direito: Valor e Tag do Pagamento
            frame_valor = ctk.CTkFrame(card_historico, fg_color="transparent")
            frame_valor.pack(side="right", anchor="e", padx=12, pady=10)

            ctk.CTkLabel(
                frame_valor,
                text=f"R$ {c.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                font=("Segoe UI", 13, "bold"),
                text_color="#4ade80"  # Verde destaque para valor
            ).pack(anchor="e")

            # Badge com a forma de pagamento
            badge = ctk.CTkFrame(frame_valor, fg_color="#1e293b", corner_radius=4)
            badge.pack(anchor="e", pady=(3, 0))

            ctk.CTkLabel(
                badge,
                text=c.metodo_pagamento.upper(),
                font=("Segoe UI", 9, "bold"),
                text_color="#60a5fa"
            ).pack(padx=6, pady=2)

    def deletar_paciente(paciente_id):
        try:
            excluir_paciente_por_id(paciente_id)
            atualizar_lista()
        except Exception:
            resultado_label_busca.configure(
                text="❌ Não é possível excluir: o paciente possui consultas registradas.",
                text_color="#f87171"
            )

    # =========================================================================
    # MODAL ÚNICO DE PACIENTE (CRIAÇÃO E EDIÇÃO)
    # =========================================================================
    def abrir_modal_paciente(paciente=None):
        eh_edicao = paciente is not None

        pop_up = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        pop_up.title("Editar Paciente" if eh_edicao else "Novo Paciente")

        # Centralização
        largura_janela, altura_janela = 400, 480
        largura_tela = pop_up.winfo_screenwidth()
        altura_tela = pop_up.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        pop_up.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        pop_up.grab_set()

        # Título Dinâmico
        ctk.CTkLabel(
            pop_up,
            text="Editar Paciente" if eh_edicao else "Cadastrar Novo Paciente",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
        ).pack(pady=(20, 15))

        # Campos de entrada
        nome_entry = ctk.CTkEntry(pop_up, width=280, height=35, placeholder_text="Nome do paciente", fg_color="#2b2b2b")
        nome_entry.pack(pady=6)

        telefone_entry = ctk.CTkEntry(pop_up, width=280, height=35, placeholder_text="Telefone", fg_color="#2b2b2b")
        telefone_entry.pack(pady=6)

        cpf_entry = ctk.CTkEntry(pop_up, width=280, height=35, placeholder_text="CPF", fg_color="#2b2b2b")
        cpf_entry.pack(pady=6)

        # Preenchimento automático se for edição
        if eh_edicao:
            nome_entry.insert(0, paciente.nome or "")
            telefone_entry.insert(0, paciente.telefone or "")
            cpf_entry.insert(0, paciente.cpf or "")

        resultado_label = ctk.CTkLabel(pop_up, text="", font=("Segoe UI", 12))
        resultado_label.pack(pady=(5, 0))

        def aplicar_correcao_nome(event):
            widget = event.widget
            texto_atual = widget.get()
            
            palavras = texto_atual.split(" ")
            excecoes = {"de", "da", "do", "dos", "das", "e"}
            
            palavras_formatadas = []
            for i, p in enumerate(palavras):
                if p.lower() in excecoes and i > 0:
                    palavras_formatadas.append(p.lower())
                else:
                    palavras_formatadas.append(p.capitalize())
                    
            texto_formatado = " ".join(palavras_formatadas)
            
            if texto_atual != texto_formatado:
                pos_cursor = widget.index(ctk.INSERT)
                widget.delete(0, "end")
                widget.insert(0, texto_formatado)
                widget.icursor(pos_cursor)

        # --- Máscaras ---
        def aplicar_mascara_cpf(event):
            texto_atual = event.widget.get()
            numeros = re.sub(r"\D", "", texto_atual)[:11]
            cpf_formatado = ""
            for i, char in enumerate(numeros):
                if i in (3, 6):
                    cpf_formatado += "."
                elif i == 9:
                    cpf_formatado += "-"
                cpf_formatado += char

            if texto_atual != cpf_formatado:
                event.widget.delete(0, "end")
                event.widget.insert(0, cpf_formatado)

        def aplicar_mascara_telefone(event):
            texto_atual = event.widget.get()
            numeros = re.sub(r"\D", "", texto_atual)[:11]
            tel_formatado = ""
            for i, char in enumerate(numeros):
                if i == 0:
                    tel_formatado += "("
                elif i == 2:
                    tel_formatado += ") "
                elif len(numeros) <= 10 and i == 6:
                    tel_formatado += "-"
                elif len(numeros) == 11 and i == 7:
                    tel_formatado += "-"
                tel_formatado += char

            if texto_atual != tel_formatado:
                event.widget.delete(0, "end")
                event.widget.insert(0, tel_formatado)
                
        nome_entry.bind("<KeyRelease>", aplicar_correcao_nome)
        cpf_entry.bind("<KeyRelease>", aplicar_mascara_cpf)
        telefone_entry.bind("<KeyRelease>", aplicar_mascara_telefone)

        # --- Validações ---
        def eh_telefone_valido(telefone: str) -> bool:
            numeros = re.sub(r"\D", "", telefone)
            if len(numeros) not in (10, 11) or len(set(numeros)) == 1:
                return False
            if len(numeros) == 11:
                ddd = int(numeros[:2])
                if ddd < 11 or ddd > 99 or ddd % 10 == 0 or numeros[2] != "9":
                    return False
            return True

        def validar():
            cpf_validator = CPF()
            nome = nome_entry.get().strip()
            cpf_str = cpf_entry.get().strip()
            telefone = telefone_entry.get().strip()

            if not nome:
                resultado_label.configure(text="❌ Insira um nome", text_color="#f87171")
                return False

            if not eh_telefone_valido(telefone):
                resultado_label.configure(text="❌ Telefone inválido", text_color="#f87171")
                return False

            if not cpf_str or not cpf_validator.validate(cpf_str):
                resultado_label.configure(text="❌ CPF inválido", text_color="#f87171")
                return False

            # No caso de edição, ignora a checagem de CPF se o CPF continuar o mesmo
            if not eh_edicao or (eh_edicao and cpf_str != paciente.cpf):
                if len(buscar_paciente_por_cpf(cpf_str)) > 0:
                    resultado_label.configure(text="❌ Já existe paciente com este CPF", text_color="#f87171")
                    return False

            return True

        def salvar():
            if validar():
                nome = nome_entry.get().strip()
                cpf_str = cpf_entry.get().strip()
                telefone = telefone_entry.get().strip()

                if eh_edicao:
                    atualizar_paciente(paciente.id, nome, telefone, cpf_str)
                else:
                    criar_paciente(nome, telefone, cpf_str)

                atualizar_lista()
                pop_up.destroy()

        # Botão com texto dinâmico
        ctk.CTkButton(
            pop_up,
            text="Atualizar Paciente" if eh_edicao else "Salvar Paciente",
            command=salvar,
            width=280,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color="#2b7a3e",
            hover_color="#1e542b",
        ).pack(pady=(20, 10))

    # =========================================================================
    # TELA PRINCIPAL (GESTAO E LISTAGEM)
    # =========================================================================
    lbl_titulo = ctk.CTkLabel(parent, text="Controle de Pacientes", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
    lbl_titulo.pack(anchor="w", padx=25, pady=(20, 10))

    frame_topo = ctk.CTkFrame(parent, fg_color="#141517", border_width=1, border_color="#242528")
    frame_topo.pack(fill="x", padx=25, pady=(0, 15))

    entry_busca = ctk.CTkEntry(
        frame_topo,
        placeholder_text="🔍 Digite Nome ou CPF para buscar...",
        height=40,
        fg_color="#212225",
        border_color="#3a3a3a",
        font=("Segoe UI", 13),
    )
    entry_busca.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=12)

    btn_novo_paciente = ctk.CTkButton(
        frame_topo,
        text="+ Criar Paciente",
        height=40,
        font=("Segoe UI", 13, "bold"),
        fg_color="#08631d",
        hover_color="#073c14",
        command=lambda: abrir_modal_paciente(),  # Abre sem parâmetro (Modo Criar)
    )
    btn_novo_paciente.pack(side="right", padx=(0, 15), pady=12)

    frame_container_lista = ctk.CTkFrame(parent, fg_color="#141517", border_width=1, border_color="#242528")
    frame_container_lista.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    resultado_label_busca = ctk.CTkLabel(frame_container_lista, text="Listando todos os pacientes", font=("Segoe UI", 12), text_color="#9ca3af")
    resultado_label_busca.pack(anchor="w", padx=15, pady=(10, 5))

    lista_frame = ctk.CTkScrollableFrame(frame_container_lista, fg_color="transparent")
    lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def atualizar_lista(lista_filtrada=None):
        for widget in lista_frame.winfo_children():
            widget.destroy()

        pacientes = lista_filtrada if lista_filtrada is not None else listar_pacientes()

        # 1. Feedback de busca / Estado vazio estilizado
        if not pacientes:
            resultado_label_busca.configure(text="❌ Nenhum paciente encontrado.", text_color="#f87171")
            
            # Estado vazio dentro da lista
            frame_vazio = ctk.CTkFrame(lista_frame, fg_color="transparent")
            frame_vazio.pack(pady=30)
            ctk.CTkLabel(
                frame_vazio,
                text="Nenhum paciente cadastrado ou encontrado.",
                font=("Segoe UI", 12, "italic"),
                text_color="#6b7280"
            ).pack()
            return

        resultado_label_busca.configure(text=f"✓ Exibindo {len(pacientes)} paciente(s).", text_color="#9ca3af")

        # 2. Renderização dos Cards dos Pacientes
        for p in pacientes:
            card = ctk.CTkFrame(
                lista_frame, 
                fg_color="#25262b", 
                border_width=1, 
                border_color="#333438", 
                corner_radius=8,
                cursor="hand2"
            )
            card.pack(fill="x", padx=5, pady=4)

            # Lado Esquerdo: Informações do Paciente
            frame_info = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
            frame_info.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            # Nome em destaque
            lbl_nome = ctk.CTkLabel(
                frame_info,
                text=f"👤 {p.nome}",
                font=("Segoe UI", 17, "bold"),
                text_color="#e5e7eb",
                cursor="hand2"
            )
            lbl_nome.pack(anchor="w")

            # CPF e Telefone estilizados
            info_secundaria = f"CPF: {p.cpf}  •  📞 {p.telefone}"
            lbl_detalhes = ctk.CTkLabel(
                frame_info,
                text=info_secundaria,
                font=("Segoe UI", 11),
                text_color="#9ca3af",
                cursor="hand2"
            )
            lbl_detalhes.pack(anchor="w", pady=(2, 0))

            # Lado Direito: Ações (Editar / Excluir)
            frame_acoes = ctk.CTkFrame(card, fg_color="transparent")
            frame_acoes.pack(side="right", padx=10, pady=10)

            btn_editar = ctk.CTkButton(
                frame_acoes, 
                text="Editar", 
                command=lambda paciente_obj=p: abrir_modal_paciente(paciente_obj),
                width=60,
                height=28,
                font=("Segoe UI", 11, "bold"),
                corner_radius=5,
                fg_color="#1e293b",
                hover_color="#334155",
                text_color="#60a5fa"
            )
            btn_editar.pack(side="left", padx=3)

            btn_excluir = ctk.CTkButton(
                frame_acoes, 
                text="❌", 
                command=lambda id_p=p.id: deletar_paciente(id_p), 
                width=28,
                height=28,
                corner_radius=5,
                fg_color="#361a1a",
                hover_color="#542323",
                text_color="#f87171"
            )
            btn_excluir.pack(side="left", padx=3)

            # --- EVENTOS DE CLIQUE PARA ABRIR O HISTÓRICO ---
            # Garante que clicar no card, no nome ou nos detalhes abre o modal
            for widget in (card, frame_info, lbl_nome, lbl_detalhes):
                widget.bind("<Button-1>", lambda event, paciente_obj=p: abrir_modal_historico(paciente_obj))

    def aplicar_mascara_busca(event):
        # Se a tecla pressionada for Backspace ou Delete, não aplica a máscara para permitir apagar
        if event.keysym in ("BackSpace", "Delete"):
            return

        widget = event.widget
        texto_atual = widget.get()
        
        # Se o texto começar com número, aplica a máscara de CPF
        if texto_atual and texto_atual[0].isdigit():
            numeros = re.sub(r"\D", "", texto_atual)[:11]
            cpf_formatado = ""
            for i, char in enumerate(numeros):
                if i in (3, 6):
                    cpf_formatado += "."
                elif i == 9:
                    cpf_formatado += "-"
                cpf_formatado += char

            if texto_atual != cpf_formatado:
                widget.delete(0, "end")
                widget.insert(0, cpf_formatado)

    def buscar_paciente(event=None):
        # Primeiramente aplica a máscara visual no campo
        aplicar_mascara_busca(event)

        termo = entry_busca.get().strip()
        if not termo:
            atualizar_lista()
            return

        apenas_numeros = re.sub(r"\D", "", termo)
        
        # Se houver números ou caracteres de CPF, realiza a busca por CPF
        if len(apenas_numeros) > 0 and (termo[0].isdigit() or "." in termo or "-" in termo):
            encontrados = buscar_paciente_por_cpf(termo)
        else:
            encontrados = buscar_paciente_por_nome(termo)

        atualizar_lista(encontrados)

    entry_busca.bind("<KeyRelease>", buscar_paciente)
    atualizar_lista()