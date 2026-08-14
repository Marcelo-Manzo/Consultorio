import re
import customtkinter as ctk
from database.models import (
    buscar_paciente_por_cpf,
    buscar_paciente_por_nome,
    criar_paciente,
    listar_pacientes,
    excluir_paciente_por_id,
)
from validate_docbr import CPF


def mostrar(parent):

    def deletar_paciente(paciente_id):
        try:
            excluir_paciente_por_id(paciente_id)
            atualizar_lista()
        except Exception as e:
            # Caso o paciente possua consultas vinculadas no banco
            resultado_label_busca.configure(
                text="❌ Não é possível excluir: o paciente possui consultas registradas.",
                text_color="#f87171"
            )

    def abrir_janela_editar():
        pass
    
    # =========================================================================
    # POP-UP DE CRIAÇÃO DE PACIENTE (CTkToplevel)
    # =========================================================================
    def abrir_layout_criar_paciente():
        pop_up = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        pop_up.title("Novo Paciente")

        # Centraliza o modal na tela
        largura_janela, altura_janela = 400, 480
        largura_tela = pop_up.winfo_screenwidth()
        altura_tela = pop_up.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))

        pop_up.geometry(
            f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}"
        )
        pop_up.grab_set()  # Mantém o foco no pop-up

        # Título do modal
        ctk.CTkLabel(
            pop_up,
            text="Cadastrar Novo Paciente",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
        ).pack(pady=(20, 15))

        # Campos de entrada no Pop-up
        nome_entry = ctk.CTkEntry(
            pop_up,
            width=280,
            height=35,
            placeholder_text="Nome do paciente",
            fg_color="#2b2b2b",
        )
        nome_entry.pack(pady=6)

        telefone_entry = ctk.CTkEntry(
            pop_up,
            width=280,
            height=35,
            placeholder_text="Telefone",
            fg_color="#2b2b2b",
        )
        telefone_entry.pack(pady=6)

        cpf_entry = ctk.CTkEntry(
            pop_up,
            width=280,
            height=35,
            placeholder_text="CPF",
            fg_color="#2b2b2b",
        )
        cpf_entry.pack(pady=6)

        resultado_label = ctk.CTkLabel(pop_up, text="", font=("Segoe UI", 12))
        resultado_label.pack(pady=(5, 0))

        # --- Máscaras Dinâmicas ---
        def aplicar_mascara_cpf(event):
            widget = event.widget
            texto_atual = widget.get()
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

        def aplicar_mascara_telefone(event):
            widget = event.widget
            texto_atual = widget.get()
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
                widget.delete(0, "end")
                widget.insert(0, tel_formatado)

        # Associa as máscaras
        cpf_entry.bind("<KeyRelease>", aplicar_mascara_cpf)
        telefone_entry.bind("<KeyRelease>", aplicar_mascara_telefone)

        # --- Validações e Cadastro ---
        def eh_telefone_valido(telefone: str) -> bool:
            numeros = re.sub(r"\D", "", telefone)
            if len(numeros) not in (10, 11) or len(set(numeros)) == 1:
                return False
            if len(numeros) == 11:
                ddd = int(numeros[:2])
                if (
                    ddd < 11
                    or ddd > 99
                    or ddd % 10 == 0
                    or numeros[2] != "9"
                ):
                    return False
            return True

        def validar():
            cpf_validator = CPF()
            nome = nome_entry.get().strip()
            cpf_str = cpf_entry.get().strip()
            telefone = telefone_entry.get().strip()

            if not nome:
                resultado_label.configure(
                    text="❌ Insira um nome", text_color="#f87171"
                )
                return False

            if not eh_telefone_valido(telefone):
                resultado_label.configure(
                    text="❌ Telefone inválido", text_color="#f87171"
                )
                return False

            if not cpf_str or not cpf_validator.validate(cpf_str):
                resultado_label.configure(
                    text="❌ CPF inválido", text_color="#f87171"
                )
                return False

            if len(buscar_paciente_por_cpf(cpf_str)) > 0:
                resultado_label.configure(
                    text="❌ Já existe paciente com este CPF",
                    text_color="#f87171",
                )
                return False

            return True

        def cadastrar():
            if validar():
                nome = nome_entry.get().strip()
                cpf = cpf_entry.get().strip()
                telefone = telefone_entry.get().strip()

                criar_paciente(nome, telefone, cpf)

                # Atualiza a lista principal e fecha o modal
                atualizar_lista()
                pop_up.destroy()

        # Botão de Ação no Pop-up (sem parênteses no command!)
        ctk.CTkButton(
            pop_up,
            text="Salvar Paciente",
            command=cadastrar,
            width=280,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color="#2b7a3e",
            hover_color="#1e542b",
        ).pack(pady=(20, 10))

    # =========================================================================
    # TELA PRINCIPAL (GESTAO E LISTAGEM)
    # =========================================================================
    lbl_titulo = ctk.CTkLabel(
        parent,
        text="Controle de Pacientes",
        font=("Segoe UI", 24, "bold"),
        text_color="#ffffff",
    )
    lbl_titulo.pack(anchor="w", padx=25, pady=(20, 10))

    # BARRA SUPERIOR (Busca e Botão Novo)
    frame_topo = ctk.CTkFrame(
        parent, fg_color="#141517", border_width=1, border_color="#242528"
    )
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
        fg_color="#2b7a3e",
        hover_color="#1e542b",
        command=abrir_layout_criar_paciente,
    )
    btn_novo_paciente.pack(side="right", padx=(0, 15), pady=12)

    # ÁREA CENTRAL (Lista / Cards)
    frame_container_lista = ctk.CTkFrame(
        parent, fg_color="#141517", border_width=1, border_color="#242528"
    )
    frame_container_lista.pack(
        fill="both", expand=True, padx=25, pady=(0, 20)
    )

    resultado_label_busca = ctk.CTkLabel(
        frame_container_lista,
        text="Listando todos os pacientes",
        font=("Segoe UI", 12),
        text_color="#9ca3af",
    )
    resultado_label_busca.pack(anchor="w", padx=15, pady=(10, 5))

    lista_frame = ctk.CTkScrollableFrame(
        frame_container_lista, fg_color="transparent"
    )
    lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    # --- Lógica de Renderização e Pesquisa na Lista ---
    def atualizar_lista(lista_filtrada=None):
        for widget in lista_frame.winfo_children():
            widget.destroy()

        pacientes = (
            lista_filtrada
            if lista_filtrada is not None
            else listar_pacientes()
        )

        if not pacientes:
            resultado_label_busca.configure(
                text="❌ Nenhum paciente encontrado.", text_color="#f87171"
            )
            return

        resultado_label_busca.configure(
            text=f"✓ Exibindo {len(pacientes)} paciente(s).", text_color="#9ca3af"
        )

        for p in pacientes:
            card = ctk.CTkFrame(
                lista_frame,
                fg_color="#212225",
                border_width=1,
                border_color="#3a3a3a",
                corner_radius=8,
            )
            card.pack(fill="x", padx=5, pady=5)

            frame_acoes = ctk.CTkFrame(card, fg_color="transparent")
            frame_acoes.pack(side="right", padx=10)

            texto = f"Nome: {p.nome}\nTelefone: {p.telefone} | CPF: {p.cpf}"
            ctk.CTkLabel(
                card,
                text=texto,
                justify="left",
                font=("Segoe UI", 12),
                text_color="#cfd0d4",
            ).pack(side="left", anchor="w", padx=12, pady=10)

            btn_editar = ctk.CTkButton(
                frame_acoes, 
                text="Editar", 
                command=abrir_janela_editar, 
                width=42,
                height=24,
                font=("Segoe UI", 10, "bold"),
                corner_radius=5,
                fg_color="#053d1c",
                hover_color="#04270d",
                text_color="#cfd0d4"
            )
            btn_editar.pack(side="left", fill="x", expand=True)

            btn_editar = ctk.CTkButton(
                frame_acoes, 
                text="❌", 
                command=lambda id_p=p.id: [deletar_paciente(id_p)], 
                width=24,
                height=24,
                corner_radius=5,
                fg_color="#361a1a",
                hover_color="#542323",
                text_color="#f87171"
            )
            btn_editar.pack(side="right", fill="x", expand=True)

    def buscar_paciente(event=None):
        termo = entry_busca.get().strip()

        if not termo:
            atualizar_lista()
            return

        # Verifica se parece busca por CPF ou por Nome
        apenas_numeros = re.sub(r"\D", "", termo)
        if len(apenas_numeros) > 0 and (
            termo[0].isdigit() or "." in termo or "-" in termo
        ):
            encontrados = buscar_paciente_por_cpf(termo)
        else:
            encontrados = buscar_paciente_por_nome(termo)

        atualizar_lista(encontrados)

    # Associa a busca ao evento de digitar
    entry_busca.bind("<KeyRelease>", buscar_paciente)

    # Carrega a lista inicial
    atualizar_lista()