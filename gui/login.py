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
            self.bg_img = ctk.CTkImage(light_image=self.bg_img_raw, dark_image=self.bg_img_raw, size=(1920, 1080))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_img, text="", bg_color="transparent")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_raw = self.bg_img_raw
        
        # 2. Login Elements - directly on background with styled form
        # Create a styled frame without rounded corners to avoid corner artifacts
        self.form_frame = ctk.CTkFrame(self, 
                                        fg_color="#1c1c1c",
                                        border_color="#4a4a4a",
                                        border_width=2,
                                        corner_radius=0)
        
        # Place at center
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Inner padding frame
        inner_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        inner_frame.pack(expand=True, fill="both", padx=45, pady=35)
        
        # Title inside form frame
        self.title_lbl = ctk.CTkLabel(inner_frame, text="Portal do Gerador", font=ctk.CTkFont(size=26, weight="bold"), text_color="white")
        self.title_lbl.pack(pady=(0, 20))
        
        # Error Label
        self.error_label = ctk.CTkLabel(inner_frame, text="", text_color="#ef4444", font=ctk.CTkFont(size=14, weight="bold"))
        self.error_label.pack(pady=(0, 15))
        
        # Username
        self.username_entry = ctk.CTkEntry(inner_frame, placeholder_text="Usuário", width=260, height=44, 
                                            corner_radius=10, border_width=2, border_color="#555555",
                                            fg_color="#2a2a2a", text_color="white", placeholder_text_color="#777777")
        self.username_entry.pack(pady=8)
        
        # Password
        self.password_entry = ctk.CTkEntry(inner_frame, placeholder_text="Senha", show="*", width=260, height=44, 
                                           corner_radius=10, border_width=2, border_color="#555555",
                                           fg_color="#2a2a2a", text_color="white", placeholder_text_color="#777777")
        self.password_entry.pack(pady=8)
        
        # Login Button
        self.login_button = ctk.CTkButton(inner_frame, text="Acessar Sistema", command=self.login_event, 
                                          width=260, height=44, corner_radius=10,
                                          font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2563eb", hover_color="#1d4ed8")
        self.login_button.pack(pady=(25, 10))
        
        # Forgot Password - below login button
        self.forgot_btn = ctk.CTkButton(inner_frame, text="Esqueci minha senha", command=self.forgot_password_event,
                                        fg_color="transparent", hover_color="#333333", text_color="#888888", font=ctk.CTkFont(size=12))
        self.forgot_btn.pack(pady=(5, 10))
        
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        if hasattr(self, 'bg_img'):
            new_size = (event.width, event.height)
            self.bg_img.configure(size=new_size)
        
    def login_event(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        
        if database.check_login(user, pwd):
            self.error_label.configure(text="")
            user_group = database.get_user_group(user)
            self.on_success(user, user_group)
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
