import customtkinter as ctk
from tkinter import messagebox
import database

class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master, current_user=None, current_user_group=None):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.current_user_group = current_user_group or 'user'
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Gestão de Usuários", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(self.header_frame, text="Cadastre novos operadores ou altere as credenciais de acesso.", text_color="gray60")
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # New User Form
        self.add_box = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=0, border_width=1, border_color="#333333")
        self.add_box.grid(row=1, column=0, sticky="ew", pady=(0, 20), padx=5)
        
        self.add_title = ctk.CTkLabel(self.add_box, text="Novo Usuário", font=ctk.CTkFont(size=16, weight="bold"))
        self.add_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.new_user_entry = ctk.CTkEntry(self.add_box, placeholder_text="Nome de Usuário", width=180, corner_radius=0)
        self.new_user_entry.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.new_pass_entry = ctk.CTkEntry(self.add_box, placeholder_text="Senha", show="*", width=150, corner_radius=0)
        self.new_pass_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        self.group_options = ["admin", "manager", "user"]
        self.group_var = ctk.CTkComboBox(self.add_box, values=self.group_options, state="readonly", width=120)
        self.group_var.set("user")
        self.group_var.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        can_add = self.current_user_group in ['admin', 'manager']
        self.add_btn = ctk.CTkButton(self.add_box, text="Cadastrar", command=self.add_user_event, corner_radius=0, width=100,
                                     fg_color="#2fa64b" if can_add else "gray", state="normal" if can_add else "disabled")
        self.add_btn.grid(row=1, column=3, padx=20, pady=10, sticky="w")
        
        if not can_add:
            ctk.CTkLabel(self.add_box, text="(Apenas admin/manager podem adicionar)", text_color="gray50", font=ctk.CTkFont(size=11))\
                .grid(row=2, column=0, columnspan=4, padx=20, pady=(0, 10), sticky="w")
        
        # User List
        self.list_box = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=0, border_width=1, border_color="#333333")
        self.list_box.grid(row=2, column=0, sticky="nsew", padx=5)
        self.list_box.grid_rowconfigure(1, weight=1)
        self.list_box.grid_columnconfigure(0, weight=1)
        
        self.list_title = ctk.CTkLabel(self.list_box, text="Usuários Ativos", font=ctk.CTkFont(size=18, weight="bold"))
        self.list_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.list_box, fg_color="transparent", corner_radius=0)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_users()

    def get_group_color(self, group):
        colors = {
            'admin': '#e74c3c',
            'manager': '#f39c12',
            'user': '#3498db'
        }
        return colors.get(group, '#3498db')

    def get_group_label(self, group):
        labels = {
            'admin': 'Administrador',
            'manager': 'Gerente',
            'user': 'Usuário'
        }
        return labels.get(group, 'Usuário')

    def load_users(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        users = database.get_all_users()
        for i, user in enumerate(users):
            user_id, username, group = user
            u_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray100", "gray20"), corner_radius=0, height=60)
            u_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
            u_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(u_frame, text=f"👤  {username}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=20, pady=15)
            
            group_color = self.get_group_color(group)
            group_label = self.get_group_label(group)
            ctk.CTkLabel(u_frame, text=group_label, text_color=group_color, font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=10, sticky="w")
            
            # Action Buttons
            btn_frame = ctk.CTkFrame(u_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, padx=10)
            
            # Todos podem alterar senha
            ctk.CTkButton(btn_frame, text="Alterar Senha", width=120, height=32, corner_radius=0,
                          command=lambda u=user_id, n=username: self.change_password_dialog(u, n)).grid(row=0, column=0, padx=5)
            
            # Apenas admin pode excluir, manager pode excluir users
            can_delete = False
            if self.current_user_group == 'admin':
                can_delete = True
            elif self.current_user_group == 'manager' and group == 'user':
                can_delete = True
            
            if username != 'admin' and can_delete:
                ctk.CTkButton(btn_frame, text="Excluir", fg_color="#8b1e1e", hover_color="#6d1818", width=80, height=32, corner_radius=0,
                              command=lambda u=user_id: self.delete_user_event(u)).grid(row=0, column=1, padx=5)

    def add_user_event(self):
        if self.current_user_group not in ['admin', 'manager']:
            messagebox.showerror("Erro", "Você não tem permissão para adicionar usuários.")
            return
            
        user = self.new_user_entry.get()
        pwd = self.new_pass_entry.get()
        group = self.group_var.get()
        
        if not user or not pwd:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        
        if self.current_user_group == 'manager' and group == 'admin':
            messagebox.showerror("Erro", "Manager não pode criar administradores.")
            return
            
        if database.add_new_user(user, pwd, group):
            messagebox.showinfo("Sucesso", f"Usuário {user} cadastrado como {group}!")
            self.new_user_entry.delete(0, 'end')
            self.new_pass_entry.delete(0, 'end')
            self.group_var.set("user")
            self.load_users()
        else:
            messagebox.showerror("Erro", "Usuário já existe.")

    def delete_user_event(self, user_id):
        if self.current_user_group not in ['admin', 'manager']:
            messagebox.showerror("Erro", "Você não tem permissão para excluir usuários.")
            return
            
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este usuário?"):
            database.delete_user(user_id)
            self.load_users()

    def change_password_dialog(self, user_id, username):
        dialog = ctk.CTkInputDialog(text=f"Nova senha para {username}:", title="Alterar Senha")
        new_pwd = dialog.get_input()
        if new_pwd:
            database.update_user_password(user_id, new_pwd)
            messagebox.showinfo("Sucesso", "Senha alterada!")