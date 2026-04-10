import customtkinter as ctk
import database
from gui.template_manager import TemplateManagerFrame
from gui.document_generator import DocumentGeneratorFrame
from gui.user_management import UserManagementFrame
from gui.image_library import ImageLibraryFrame
from gui.settings import SettingsFrame

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_logout, current_user=None, current_user_group='user'):
        super().__init__(master, corner_radius=0)
        self.on_logout = on_logout
        self.current_user = current_user
        self.current_user_group = current_user_group
        
        # Load theme from DB
        current_theme = database.get_setting("theme", "dark")
        ctk.set_appearance_mode(current_theme)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#3B8ED0", "#1f538d"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DocGen Pro v2.0", text_color="white", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
        
        # Menu Options
        self.btn_gen = self._create_menu_btn("📄  Gerar Documento", self.show_generator, 1)
        self.btn_man = self._create_menu_btn("⚙️  Gerenciar Modelos", self.show_manager, 2)
        self.btn_img = self._create_menu_btn("🖼️  Biblioteca de Imagens", self.show_images, 3)
        self.btn_users = self._create_menu_btn("👥  Gerenciar Usuários", self.show_users, 4)
        
        # Configurações apenas para admin/manager
        if self.current_user_group in ['admin', 'manager']:
            self.btn_settings = self._create_menu_btn("⚙️  Configurações", self.show_settings, 5)
            self.bottom_row = 7
        else:
            self.btn_settings = None
            self.bottom_row = 5
        
        # Bottom area (Theme Toggle + Logout)
        self.bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bottom_frame.grid(row=self.bottom_row, column=0, padx=15, pady=20, sticky="s")
        
        self.theme_var = ctk.StringVar(value="Modo Escuro" if current_theme == "dark" else "Modo Claro")
        self.theme_switch = ctk.CTkSwitch(self.bottom_frame, text=self.theme_var.get(), command=self.toggle_theme,
                                          progress_color="#1a1a1a", text_color="white", width=120)
        self.theme_switch.pack(pady=10)
        if current_theme == "dark": self.theme_switch.select()
        
        self.user_info = ctk.CTkLabel(self.bottom_frame, text=f"Olá, {current_user} ({current_user_group})", 
                                       text_color="gray", font=ctk.CTkFont(size=10))
        self.user_info.pack(pady=(0, 5))
        
        self.btn_logout = ctk.CTkButton(self.bottom_frame, text="Sair do Sistema", command=self.on_logout, 
                                        fg_color="transparent", hover_color="#8b1e1e",
                                        text_color="white", border_width=1, border_color="white", height=38, corner_radius=0)
        self.btn_logout.pack(pady=10, fill="x")
        
        # Main View container
        self.main_view = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_view.grid_rowconfigure(0, weight=1)
        self.main_view.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        self.show_generator()
        
    def _create_menu_btn(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, command=command,
                             anchor="w", height=45, fg_color="transparent", text_color="white",
                             hover_color="#2b6fb0", font=ctk.CTkFont(size=14, weight="bold"))
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def toggle_theme(self):
        new_mode = "dark" if self.theme_switch.get() == 1 else "light"
        ctk.set_appearance_mode(new_mode)
        database.save_setting("theme", new_mode)
        self.theme_var.set("Modo Escuro" if new_mode == "dark" else "Modo Claro")
        self.theme_switch.configure(text=self.theme_var.get())

    def reset_buttons(self):
        buttons = [self.btn_gen, self.btn_man, self.btn_img, self.btn_users]
        if self.btn_settings:
            buttons.append(self.btn_settings)
        for b in buttons:
            b.configure(fg_color="transparent", text_color="white")
        
    def set_active_button(self, btn):
        self.reset_buttons()
        btn.configure(fg_color="white", text_color=("#1f538d", "#1f538d"))

    def show_generator(self):
        if self.current_frame: self.current_frame.destroy()
        self.set_active_button(self.btn_gen)
        self.current_frame = DocumentGeneratorFrame(self.main_view)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
    def show_manager(self):
        if self.current_frame: self.current_frame.destroy()
        self.set_active_button(self.btn_man)
        self.current_frame = TemplateManagerFrame(self.main_view)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_images(self):
        if self.current_frame: self.current_frame.destroy()
        self.set_active_button(self.btn_img)
        self.current_frame = ImageLibraryFrame(self.main_view)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
    def show_users(self):
        if self.current_frame: self.current_frame.destroy()
        self.set_active_button(self.btn_users)
        self.current_frame = UserManagementFrame(self.main_view, self.current_user, self.current_user_group)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
    def show_settings(self):
        if self.current_user_group not in ['admin', 'manager']:
            return
        if self.current_frame: self.current_frame.destroy()
        self.set_active_button(self.btn_settings)
        self.current_frame = SettingsFrame(self.main_view)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
    def refresh_all(self):
        current_btn = None
        if self.current_frame:
            if isinstance(self.current_frame, DocumentGeneratorFrame):
                current_btn = self.btn_gen
            elif isinstance(self.current_frame, TemplateManagerFrame):
                current_btn = self.btn_man
            elif isinstance(self.current_frame, ImageLibraryFrame):
                current_btn = self.btn_img
            elif isinstance(self.current_frame, UserManagementFrame):
                current_btn = self.btn_users
            elif isinstance(self.current_frame, SettingsFrame):
                current_btn = self.btn_settings
        
        if current_btn == self.btn_gen:
            self.show_generator()
        elif current_btn == self.btn_man:
            self.show_manager()
        elif current_btn == self.btn_img:
            self.show_images()
        elif current_btn == self.btn_users:
            self.show_users()
        elif current_btn == self.btn_settings:
            self.show_settings()
        else:
            self.show_generator()
