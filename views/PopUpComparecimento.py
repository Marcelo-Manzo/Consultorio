import customtkinter as ctk
from database.models import buscar_consulta_Atual, marcar_comparecimento
from datetime import datetime

def mostrar(parent):
    """
    Função principal que gerencia o pop-up de notificação.
    Recebe 'parent' (a janela principal do app) para poder centralizar o pop-up corretamente.
    """
    
    def abrir_notificacao_comparecimento(data_e_horario):
        # 1. Busca os dados da consulta que disparou o alarme
        consulta = buscar_consulta_Atual(data_e_horario)
        
        # Se por algum motivo não achar a consulta, cancela para não dar erro na tela
        if not consulta:
            return

        # 2. Criação da Janela Pop-up (Toplevel)
        popup = ctk.CTkToplevel(parent, fg_color="#1e1f22")
        popup.title("Confirmação de Horário")
        
        # Configurações de tamanho e centralização na tela
        largura_janela = 420
        altura_janela = 200
        largura_tela = popup.winfo_screenwidth()
        altura_tela = popup.winfo_screenheight()
        posicao_x = int((largura_tela / 2) - (largura_janela / 2))
        posicao_y = int((altura_tela / 2) - (altura_janela / 2))
        
        popup.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
        popup.resizable(False, False)
        
        # Faz a janela ficar por cima de tudo e captura o foco (modal)
        popup.attributes("-topmost", True)
        popup.grab_set()

        #==================== FUNÇÕES DE AÇÃO ====================
        def responder_sim():
            # Status 1 = Compareceu
            marcar_comparecimento(consulta["id"], status=1)
            popup.destroy()
            # Se você tiver uma função global para recarregar a agenda na tela de fundo, chame-a aqui
            print(f"Consulta {consulta['id']} marcada como COMPARECEU.")

        def responder_nao():
            # Status 2 = Faltou (vai direto para a aba de faltantes)
            marcar_comparecimento(consulta["id"], status=2)
            popup.destroy()
            print(f"Consulta {consulta['id']} marcada como FALTA.")

        #==================== ELEMENTOS VISUAIS ====================
        
        # Ícone sutil ou Header de Alerta
        lbl_alerta = ctk.CTkLabel(popup, text="⏰ HORÁRIO DA CONSULTA", font=("Segoe UI", 11, "bold"), text_color="#1f6aa5")
        lbl_alerta.pack(pady=(15, 5))

        # Formatação do horário para exibição amigável
        # (Ajuste o formato caso seu banco retorne string ou objeto datetime direto)
        horario_formatado = consulta["data"].strftime("%H:%M") if isinstance(consulta["data"], datetime) else str(consulta["data"])[11:16]

        # Texto Principal com o Nome do Paciente e Tratamento
        texto_pergunta = f"O paciente {consulta['nome'].split()[0]} chegou para a consulta de {consulta['tratamento']} das {horario_formatado}?"
        
        lbl_pergunta = ctk.CTkLabel(
            popup, 
            text=texto_pergunta, 
            font=("Segoe UI", 14), 
            text_color="#ffffff",
            wraplength=380, # Faz o texto quebrar linha sozinho se o nome for grande
            justify="center"
        )
        lbl_pergunta.pack(pady=(5, 20), padx=20)

        # Container para colocar os botões lado a lado
        frame_botoes = ctk.CTkFrame(popup, fg_color="transparent")
        frame_botoes.pack(pady=5)

        # BOTÃO NÃO: Estilo mais discreto/cinza escuro, focado em cancelar
        btn_nao = ctk.CTkButton(
            frame_botoes, 
            text="Não compareceu", 
            command=responder_nao,
            width=150,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            text_color="#ff4a4a" # Texto em vermelho para dar a pista visual do erro/falta
        )
        btn_nao.pack(side="left", padx=10)

        # BOTÃO SIM: Destacado em verde ou azul padrão do sistema
        btn_sim = ctk.CTkButton(
            frame_botoes, 
            text="Sim, compareceu", 
            command=responder_sim,
            width=150,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#1a3a22", # Verde escuro cirúrgico/sutil
            hover_color="#122818",
            text_color="#2ecc71" # Texto verde claro brilhante para sucesso
        )
        btn_sim.pack(side="left", padx=10)

    # Retorna a função interna caso você precise chamá-la de fora mapeando o relógio
    return abrir_notificacao_comparecimento