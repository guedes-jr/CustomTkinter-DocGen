import customtkinter as ctk
from tkinter import filedialog, messagebox
import database
import os

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text="Configurações do Software", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.db_path_label = ctk.CTkLabel(self.content_frame, text="Arquivo do Banco de Dados SQLite:", font=ctk.CTkFont(size=14, weight="bold"))
        self.db_path_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.path_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.path_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.current_path = database.get_setting('db_path', 'database.db')
        self.path_entry = ctk.CTkEntry(self.path_frame, placeholder_text=self.current_path)
        self.path_entry.insert(0, self.current_path)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.path_frame, text="Procurar", command=self.browse_file, width=100)
        self.btn_browse.grid(row=0, column=1)
        
        self.info_label = ctk.CTkLabel(self.content_frame, text="Selecione um arquivo .db ou .sqlite.\nPara usar em rede compartilhada, selecione um arquivo em pasta sincronizada (Dropbox, Google Drive, OneDrive).", 
                                        text_color="gray", font=ctk.CTkFont(size=12))
        self.info_label.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="w")
        
        self.lock_status_label = ctk.CTkLabel(self.content_frame, text="Status do Banco:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lock_status_label.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.check_lock_status()
        
        self.btn_save = ctk.CTkButton(self.content_frame, text="Salvar e Aplicar", command=self.save_settings, fg_color="#2fa64b")
        self.btn_save.grid(row=5, column=0, padx=20, pady=20, sticky="e")
        
        self.current_db_label = ctk.CTkLabel(self.content_frame, text="", text_color="gray", font=ctk.CTkFont(size=11))
        self.current_db_label.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="w")
        self.update_current_db_label()
        
    def browse_file(self):
        file = filedialog.askopenfilename(
            title="Selecionar arquivo do banco de dados",
            filetypes=[("SQLite Database", "*.db"), ("SQLite Database", "*.sqlite"), ("All Files", "*.*")]
        )
        if file:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file)
    
    def update_current_db_label(self):
        self.current_db_label.configure(text=f"Banco atual: {database.DB_PATH}")
    
    def check_lock_status(self):
        result = database.is_process_running()
        if result is True:
            self.lock_status = ctk.CTkLabel(self.content_frame, text="✓ Livre - Nenhum outro processo usando o banco", text_color="green")
        else:
            hostname = result if isinstance(result, str) else "desconhecido"
            self.lock_status = ctk.CTkLabel(self.content_frame, text=f"⚠ Bloqueado por: {hostname}", text_color="orange")
        self.lock_status.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        self.after(5000, self.check_lock_status)
    
    def save_settings(self):
        new_path = self.path_entry.get().strip()
        
        if not new_path:
            messagebox.showerror("Erro", "Caminho do banco não pode ser vazio.")
            return
        
        ext = os.path.splitext(new_path)[1].lower()
        if ext not in ['.db', '.sqlite']:
            messagebox.showerror("Erro", "Arquivo deve ter extensão .db ou .sqlite")
            return
        
        if not os.path.exists(new_path):
            create = messagebox.askyesno("Banco não existe", "O arquivo não existe. Deseja criar um novo banco?")
            if not create:
                return
        
        database.set_db_path(new_path)
        self.update_current_db_label()
        messagebox.showinfo("Sucesso", f"Banco alterado para: {new_path}")