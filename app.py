import customtkinter as ctk
from views import pacientes, consultas, agenda_Semanal, faltantes
from database.models import buscar_consulta_Atual
# IMPORTANTE: Importa a função do pop-up e a busca do banco de dados
from views.PopUpComparecimento import mostrar as mostrar_popup_comparecimento
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# horarios_padrao = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Consultório")
        self.geometry("900x600")
        
        # Frame lateral com botões de navegação
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#111214")
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        self.titulo = ctk.CTkLabel(self.sidebar, text="Menu", font=("Arial", 20, "bold"))
        self.titulo.pack(pady=20)
        
        ctk.CTkButton(
            self.sidebar,
            text="Pacientes",
            command=self.mostrar_pacientes,
            width=180
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Consultas",
            command=self.mostrar_consultas,
            width=180
        ).pack(pady=10)
        
        ctk.CTkButton(
            self.sidebar,
            text="agenda",
            command=self.mostrar_agenda_semanal,
            width=180
        ).pack(pady=10)
        
        ctk.CTkButton(
            self.sidebar,
            text="Faltantes",
            command=self.mostrar_faltantes,
            width=180
        ).pack(pady=10)
                
        # Frame principal onde as telas aparecem
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.disparar_popup = mostrar_popup_comparecimento(self)
        # Inicia mostrando a tela de agenda
        self.mostrar_agenda_semanal()
        
        # 🚀 DA A PARTIDA NO RELÓGIO: Inicia o loop de verificação de consultas
        self.verificar_horarios_consultas()
    
    # ==================== SEGUNDO PLANO (RELÓGIO) ====================

    def obter_bloco_horario_atual(self):
        agora = datetime.now()
        # Se os minutos forem menores que 30, o bloco é '00'. Se forem maiores, o bloco é '30'.
        minuto_bloco = 0 if agora.minute < 30 else 30
        
        # Retorna a data de hoje com a hora atual, mas cravada no bloco (00 ou 30) e SEM segundos
        return datetime(agora.year, agora.month, agora.day, agora.hour, minuto_bloco, 0)
    
    def verificar_horarios_consultas(self):
        # Descobre o bloco de 30 min atual (ex: 2026-07-01 15:30:00)
        bloco_atual = self.obter_bloco_horario_atual()

        # Busca no banco usando o horário cravado do bloco
        consulta_no_bloco = buscar_consulta_Atual(bloco_atual)
        
        # Se achar e ela ainda for status 0, o pop-up abre
        if consulta_no_bloco:
           self.disparar_popup(consulta_no_bloco["data"])
            
        # Pode rodar a checagem a cada 5 minutos (300000 ms) em vez de 1 minuto!
        self.after(300000, self.verificar_horarios_consultas)
    
    # ==================== GERENCIAMENTO DE TELAS ====================
    def limpar_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
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