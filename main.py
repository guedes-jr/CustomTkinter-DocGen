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
        self.state('zoomed')
        
        database.init_db()
        database.set_on_db_change(self.on_db_changed)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.current_user = None
        self.current_user_group = None
        self.dashboard_frame = None
        self.show_login()

    def on_db_changed(self):
        if self.dashboard_frame:
            self.dashboard_frame.refresh_all()
        
    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def on_login_success(self, username, user_group):
        self.current_user = username
        self.current_user_group = user_group
        
        for widget in self.winfo_children():
            widget.destroy()
            
        self.dashboard_frame = DashboardFrame(self, self.on_logout, self.current_user, self.current_user_group)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_logout(self):
        self.current_user = None
        self.current_user_group = None
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()
