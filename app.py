import customtkinter as ctk
from views import pacientes, consultas, agenda_Semanal, faltantes
# Importa a biblioteca CustomTkinter e os módulos de views que contêm as telas.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    # Cria a classe principal do app que herda de CTk (a janela principal).
    def __init__(self):
        super().__init__()
        # __init__ é o construtor — roda quando você cria App().
        
        self.title("Consultório")
        self.geometry("900x600")
        
        # Frame lateral com botões de navegação (CORRIGIDO: adicionado fg_color para contraste profundo)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#111214")
                                    # fill y preenche verticalmente
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        # Cria o menu lateral — um frame (caixa) de 200px de largura, cantos retos (corner_radius=0). O .pack(side="left", fill="y") coloca ele na esquerda e preenche verticalmente.
        
        self.titulo = ctk.CTkLabel(self.sidebar, text="Menu", font=("Arial", 20, "bold"))
        self.titulo.pack(pady=20)
        # Cria o texto "Menu" dentro do sidebar, fonte Arial 20px negrito, com 20px de espaçamento vertical.
        
        ctk.CTkButton(
            self.sidebar,
            text="Pacientes",
            command=self.mostrar_pacientes,
            width=180
        ).pack(pady=10)
        # Cria o botão "Pacientes". Quando clicado, executa self.mostrar_pacientes. O .pack(pady=10) coloca o botão na tela com 10px de espaçamento.

        ctk.CTkButton(
            self.sidebar,
            text="Consultas",
            command=self.mostrar_consultas,
            width=180
        ).pack(pady=10)
        #botao das consultas
        ctk.CTkButton(
            self.sidebar,
            text="agenda",
            command=self.mostrar_agenda_semanal,
            width=180
        ).pack(pady=10)
        #agenda
        ctk.CTkButton(
            self.sidebar,
            text="Faltantes",
            command=self.mostrar_faltantes,
            width=180
        ).pack(pady=10)
                
        
        # Frame principal onde as telas aparecem (CORRIGIDO: fg_color="transparent" para profundidade visual)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
                                          #preenche todo o resto horizontal e vertical
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        # Cria o frame principal (área grande à direita) onde as telas de Pacientes e Consultas vão aparecer. fill="both" + expand=True fazem ele ocupar todo o espaço disponível.
        
        # Inicia mostrando a tela de pacientes
        self.mostrar_agenda_semanal()
    
    # Remove todos os elementos dentro do main_frame. Isso é necessário antes de trocar de tela — senão os elementos se acumulam um em cima do outro
    def limpar_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    # Limpa o frame e chama a função mostrar() do módulo pacientes, passando o main_frame como container.
    def mostrar_pacientes(self):
        self.limpar_frame()
        pacientes.mostrar(self.main_frame)
    
    def mostrar_consultas(self):
        self.limpar_frame()
        consultas.mostrar(self.main_frame)
    
    def mostrar_agenda_semanal(self):
        self.limpar_frame()
        agenda_Semanal.mostrar(self.main_frame)

    def mostrar_faltantes(self):
        self.limpar_frame()
        faltantes.mostrar(self.main_frame)

    


if __name__ == "__main__":
    app = App()
    app.mainloop()
