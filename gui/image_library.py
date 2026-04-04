import customtkinter as ctk
from tkinter import filedialog, messagebox
import database
import os
from PIL import Image

class ImageLibraryFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Biblioteca de Imagens", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(self.header_frame, text="Gerencie assinaturas e logotipos para inserção rápida em seus modelos.", text_color="gray60")
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Add Image Box
        self.add_box = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=0, border_width=1, border_color="#333333")
        self.add_box.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        lbl_add = ctk.CTkLabel(self.add_box, text="Novo Ativo:", font=ctk.CTkFont(weight="bold"))
        lbl_add.grid(row=0, column=0, padx=20, pady=15)
        
        self.name_entry = ctk.CTkEntry(self.add_box, placeholder_text="Ex: Assinatura Diretor", width=250, corner_radius=0)
        self.name_entry.grid(row=0, column=1, padx=10, pady=15)
        
        self.path_btn = ctk.CTkButton(self.add_box, text="Selecionar Arquivo", command=self.pick_file, corner_radius=0)
        self.path_btn.grid(row=0, column=2, padx=10, pady=15)
        
        self.selected_path = None
        self.file_lbl = ctk.CTkLabel(self.add_box, text="Nenhum arquivo...", text_color="gray50")
        self.file_lbl.grid(row=0, column=3, padx=10, pady=15)
        
        self.save_btn = ctk.CTkButton(self.add_box, text="💾 Salvar na Biblioteca", command=self.save_image, corner_radius=0, fg_color="#1f538d")
        self.save_btn.grid(row=0, column=4, padx=20, pady=15)
        
        # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray15"), corner_radius=0, border_width=1, border_color="#333333")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_images()

    def pick_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filepath:
            self.selected_path = filepath
            self.file_lbl.configure(text=os.path.basename(filepath)[:20])

    def save_image(self):
        name = self.name_entry.get()
        if not name or not self.selected_path:
            messagebox.showwarning("Aviso", "Preencha o nome e selecione um arquivo.")
            return
            
        database.add_library_image(name, self.selected_path)
        messagebox.showinfo("Sucesso", "Imagem adicionada à biblioteca!")
        self.name_entry.delete(0, 'end')
        self.selected_path = None
        self.file_lbl.configure(text="Nenhum arquivo...")
        self.load_images()

    def load_images(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        images = database.get_library_images()
        for i, img_data in enumerate(images):
            img_id, name, path = img_data
            
            card = ctk.CTkFrame(self.scroll_frame, fg_color=("white", "gray20"), corner_radius=0)
            card.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            card.grid_columnconfigure(1, weight=1)
            
            # Icon/Preview placeholder or icon
            lbl_name = ctk.CTkLabel(card, text=f"🖼️  {name}", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_name.grid(row=0, column=0, padx=20, pady=15, sticky="w")
            
            lbl_path = ctk.CTkLabel(card, text=path, text_color="gray50", font=ctk.CTkFont(size=11))
            lbl_path.grid(row=0, column=1, padx=20, pady=15, sticky="w")
            
            btn_del = ctk.CTkButton(card, text="Excluir", fg_color="#8b1e1e", hover_color="#6d1818", width=80, corner_radius=0,
                                     command=lambda u=img_id: self.delete_image_event(u))
            btn_del.grid(row=0, column=2, padx=20, pady=15)

    def delete_image_event(self, img_id):
        if messagebox.askyesno("Confirmar", "Remover esta imagem da biblioteca?"):
            database.delete_library_image(img_id)
            self.load_images()
