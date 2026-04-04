import customtkinter as ctk
from gui.login import LoginFrame
from gui.dashboard import DashboardFrame
import database

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Documentos")
        self.geometry("1100x700")
        
        database.init_db()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def on_login_success(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.dashboard_frame = DashboardFrame(self, self.on_logout)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_logout(self):
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()
