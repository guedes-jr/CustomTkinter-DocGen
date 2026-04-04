import customtkinter as ctk
from tkinter import messagebox
import database
from PIL import Image
import os
import webbrowser

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color="transparent")
        self.on_success = on_success
        
        # Grid layout for background
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Load background image
        bg_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'login_bg.png')
        if os.path.exists(bg_path):
            self.bg_img_raw = Image.open(bg_path)
            self.bg_img = ctk.CTkImage(light_image=self.bg_img_raw, dark_image=self.bg_img_raw, size=(1280, 720))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_img, text="")
            self.bg_label.grid(row=0, column=0, rowspan=10, sticky="nsew")
        
        # 2. Main Login Elements (Directly in self for transparency)
        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            img = ctk.CTkImage(light_image=Image.open(logo_path),
                               dark_image=Image.open(logo_path),
                               size=(140, 140))
            self.logo_label = ctk.CTkLabel(self, text="", image=img)
            self.logo_label.grid(row=1, column=0, pady=(0, 20))
        else:
            self.logo_label = ctk.CTkLabel(self, text="DocGen Pro", font=ctk.CTkFont(size=36, weight="bold"), text_color="white")
            self.logo_label.grid(row=1, column=0, pady=(0, 20))
            
        self.title_lbl = ctk.CTkLabel(self, text="Portal do Gerador", font=ctk.CTkFont(size=30, weight="bold"), text_color="white")
        self.title_lbl.grid(row=2, column=0, pady=(0, 10))
        
        # ERROR LABEL
        self.error_label = ctk.CTkLabel(self, text="", text_color="#ef4444", font=ctk.CTkFont(size=14, weight="bold"))
        self.error_label.grid(row=3, column=0, pady=(0, 15))
        
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Usuário", width=350, height=55, corner_radius=0, border_width=0, fg_color="#1a1a1a")
        self.username_entry.grid(row=4, column=0, pady=12)
        
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=350, height=55, corner_radius=0, border_width=0, fg_color="#1a1a1a")
        self.password_entry.grid(row=5, column=0, pady=12)
        
        # Forgot Password
        self.forgot_btn = ctk.CTkButton(self, text="Esqueci minha senha", command=self.forgot_password_event,
                                        fg_color="transparent", hover_color=None, text_color="#AAAAAA", font=ctk.CTkFont(size=12, underline=True), width=100)
        self.forgot_btn.grid(row=6, column=0, sticky="e", padx=(0, 370)) # Adjusted for centering relative to entries
        
        self.login_button = ctk.CTkButton(self, text="Acessar Sistema", command=self.login_event, width=350, height=55, corner_radius=0, font=ctk.CTkFont(size=18, weight="bold"))
        self.login_button.grid(row=7, column=0, pady=(40, 0))
        
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        if hasattr(self, 'bg_img'):
            self.bg_img.configure(size=(event.width, event.height))
        
    def login_event(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        
        if database.check_login(user, pwd):
            self.error_label.configure(text="")
            self.on_success()
        else:
            self.error_label.configure(text="❌ Usuário ou senha incorretos!")
            
    def forgot_password_event(self):
        user = self.username_entry.get()
        if not user:
            messagebox.showwarning("Recuperação", "Por favor, digite seu nome de usuário no campo acima para solicitar a recuperação.")
            return
            
        # Simulação de envio de e-mail / Abertura de Log para juniorgmj2016@gmail.com
        target_email = "juniorgmj2016@gmail.com"
        subject = "Recuperacao de Acesso - DocGen Pro"
        body = f"Solicitação de recuperação para o usuário: {user}"
        
        # Modo fallback: Abrir cliente de e-mail local (Seguro sem precisar de SMTP creds)
        mailto_url = f"mailto:{target_email}?subject={subject}&body={body}"
        
        try:
            webbrowser.open(mailto_url)
            messagebox.showinfo("Solicitação Enviada", f"Uma solicitação de recuperação para o usuário '{user}' foi enviada para {target_email}.\nVerifique seu cliente de e-mail.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o cliente de e-mail: {e}")
