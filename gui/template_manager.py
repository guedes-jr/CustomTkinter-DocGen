import customtkinter as ctk
import shutil
import os
from tkinter import filedialog, messagebox
import database

class TemplateManagerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Gerenciar Modelos", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(self.header_frame, text="Adicione e visualize os documentos Word (.docx) que servirão de base para o sistema.", text_color="gray60")
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Action buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        self.add_btn = ctk.CTkButton(self.btn_frame, text="+ Adicionar Novo Modelo", font=ctk.CTkFont(weight="bold"), 
                                     command=self.add_template, height=40)
        self.add_btn.pack(side="left", padx=(0, 10))
        
        # Scrollable Box for List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray15"), corner_radius=0)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_templates()
        
    def load_templates(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        templates = database.get_templates()
        if not templates:
            lbl = ctk.CTkLabel(self.scroll_frame, text="Nenhum modelo cadastrado no momento.\nAdicione o seu primeiro clicando no botão acima!", text_color="gray50")
            lbl.grid(row=0, column=0, padx=20, pady=40)
            return

        for i, t in enumerate(templates):
            card = ctk.CTkFrame(self.scroll_frame, fg_color=("gray100", "gray20"), corner_radius=0)
            card.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            card.grid_columnconfigure(1, weight=1)
            
            icon = ctk.CTkLabel(card, text="📄", font=ctk.CTkFont(size=28))
            icon.grid(row=0, column=0, padx=(15, 10), pady=15)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="w")
            
            title = ctk.CTkLabel(info_frame, text=t[1], font=ctk.CTkFont(size=16, weight="bold"))
            title.grid(row=0, column=0, sticky="w")
            
            path_lbl = ctk.CTkLabel(info_frame, text="Gerenciado pelo sistema de templates rápidos", text_color="gray50", font=ctk.CTkFont(size=12))
            path_lbl.grid(row=1, column=0, sticky="w")
            
            actions_frame = ctk.CTkFrame(card, fg_color="transparent")
            actions_frame.grid(row=0, column=2, padx=10)
            
            download_btn = ctk.CTkButton(actions_frame, text="📥 Planilha", command=lambda t_id=t[0], t_name=t[1]: self.download_template_spreadsheet(t_id, t_name),
                                         width=100, height=30, font=ctk.CTkFont(size=12))
            download_btn.pack(side="left", padx=2)
            
            delete_btn = ctk.CTkButton(actions_frame, text="🗑️", command=lambda t_id=t[0]: self.delete_template(t_id),
                                       width=40, height=30, fg_color="#c0392b", hover_color="#e74c3c")
            delete_btn.pack(side="left", padx=2)
            
    def download_template_spreadsheet(self, template_id, template_name):
        from utils.docx_parser import extract_variables
        
        templates = database.get_templates()
        template_path = None
        for t in templates:
            if t[0] == template_id:
                template_path = t[2]
                break
        
        if not template_path or not os.path.exists(template_path):
            messagebox.showerror("Erro", "Arquivo do modelo não encontrado.")
            return
        
        variables = extract_variables(template_path)
        if not variables:
            messagebox.showwarning("Aviso", "Não foram encontradas variáveis no modelo.")
            return
        
        import pandas as pd
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"modelo_{template_name.replace('.docx', '')}.xlsx"
        )
        
        if save_path:
            try:
                df = pd.DataFrame(columns=variables)
                df.to_excel(save_path, index=False, engine='openpyxl')
                messagebox.showinfo("Sucesso", f"Planilha modelo salva em:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao criar planilha: {e}")
    
    def delete_template(self, template_id):
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este modelo?"):
            try:
                database.delete_template(template_id)
                self.load_templates()
                messagebox.showinfo("Sucesso", "Modelo excluído!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {e}")
            
    def add_template(self):
        filepath = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if filepath:
            filename = os.path.basename(filepath)
            dest_dir = os.path.join(database.get_appdata_dir(), "templates_dir")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            
            try:
                shutil.copy(filepath, dest_path)
                database.add_template(filename, dest_path)
                messagebox.showinfo("Sucesso", "Modelo adicionado com sucesso!")
                self.load_templates()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao adicionar modelo: {e}")
