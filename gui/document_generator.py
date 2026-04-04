import customtkinter as ctk
import os
import json
import time
import pandas as pd
from datetime import datetime
from tkinter import filedialog, messagebox
import database
from utils import docx_parser
from tkcalendar import DateEntry
import shutil

class VariableInputRow(ctk.CTkFrame):
    def __init__(self, master, var_name, preload_data=None):
        super().__init__(master, fg_color="transparent")
        self.var_name = var_name
        self.type_var = ctk.StringVar(value="Texto")
        
        # Space Between Layout
        self.grid_columnconfigure(1, weight=1) # Spacer between label and controls
        
        self.lbl = ctk.CTkLabel(self, text=var_name.upper() + ":", font=ctk.CTkFont(weight="bold"), width=180, anchor="w")
        self.lbl.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")
        
        # Tooltip / Desc button
        self.desc_btn = ctk.CTkButton(self, text="❓", width=30, height=30, fg_color="transparent", 
                                       text_color="gray", hover_color="#333333", command=self.show_desc_dialog)
        self.desc_btn.grid(row=0, column=0, padx=(170, 0), sticky="w")
        
        # Right aligned container for controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=0, column=2, sticky="e", padx=(0, 10), pady=5)
        self.controls_frame.grid_columnconfigure(0, weight=0) # Type menu
        self.controls_frame.grid_columnconfigure(1, weight=1) # Input area
        
        self.types_list = ["Texto", "Inteiro Positivo", "Decimal", "Tempo (Hora)", "Data", "Data e Hora", "Imagem"]
        self.type_menu = ctk.CTkOptionMenu(self.controls_frame, variable=self.type_var, values=self.types_list, 
            width=140, command=self.on_type_change)
        self.type_menu.grid(row=0, column=0, padx=10, pady=5)
        
        self.input_container = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.input_container.grid(row=0, column=1, sticky="e", padx=10, pady=5)
        
        self.current_value_getter = None
        self.current_state_getter = None
        self.selected_image_path = None
        
        if preload_data and "ui_type" in preload_data and preload_data["ui_type"] in self.types_list:
            self.type_var.set(preload_data["ui_type"])
            self.on_type_change(preload_data["ui_type"], preload_data)
        else:
            self.on_type_change("Texto")
            
    def show_desc_dialog(self):
        current_desc = database.get_var_desc(self.var_name)
        dialog = ctk.CTkInputDialog(text=f"Descrição para '{self.var_name}':\n(Atualmente: {current_desc or 'Nenhuma'})", title="Metadados")
        new_desc = dialog.get_input()
        if new_desc is not None:
            database.save_var_desc(self.var_name, new_desc)
            messagebox.showinfo("Sucesso", "Descrição salva!")

    def _apply_mask(self, event, entry, mask_type):
        if mask_type == "Nenhum": return
        val = entry.get()
        # Simple CPF mask simulation
        if mask_type == "CPF":
            clean = "".join(filter(str.isdigit, val))
            if len(clean) > 11: clean = clean[:11]
            fmt = clean
            if len(clean) > 3: fmt = clean[:3] + "." + clean[3:]
            if len(clean) > 6: fmt = fmt[:7] + "." + fmt[7:]
            if len(clean) > 9: fmt = fmt[:11] + "-" + fmt[11:]
            entry.delete(0, 'end')
            entry.insert(0, fmt)
            
    def on_type_change(self, new_type, preload_data=None):
        for widget in self.input_container.winfo_children():
            widget.destroy()
            
        self.selected_image_path = preload_data.get("raw_val") if preload_data else None
            
        if new_type in ["Texto", "Inteiro Positivo", "Decimal"]:
            f = ctk.CTkFrame(self.input_container, fg_color="transparent")
            f.grid(row=0, column=0, sticky="e")
            
            ent = ctk.CTkEntry(f, width=280, height=38, corner_radius=0)
            ent.grid(row=0, column=0, sticky="e")
            
            mask_var = ctk.StringVar(value=preload_data.get("mask", "Nenhum") if preload_data else "Nenhum")
            if new_type == "Texto":
                mask_menu = ctk.CTkOptionMenu(f, variable=mask_var, values=["Nenhum", "CPF", "CNPJ", "Moeda (R$)"], width=100)
                mask_menu.grid(row=0, column=1, padx=(10, 0))
                ent.bind("<KeyRelease>", lambda e: self._apply_mask(e, ent, mask_var.get()))
            
            if new_type == "Texto": ent.configure(placeholder_text="Texto Livre")
            elif new_type == "Inteiro Positivo": ent.configure(placeholder_text="123")
            elif new_type == "Decimal": ent.configure(placeholder_text="10.50")
            
            if preload_data and preload_data.get("raw_val"):
                ent.insert(0, preload_data["raw_val"])
                
            def base_val_getter():
                val = ent.get()
                if new_type == "Inteiro Positivo": return ''.join(filter(str.isdigit, val))
                if new_type == "Decimal": return val.replace(",", ".")
                return val

            self.current_value_getter = lambda: {"type": "texto", "value": base_val_getter()}
            self.current_state_getter = lambda: {"ui_type": new_type, "raw_val": ent.get(), "mask": mask_var.get() if new_type=="Texto" else "Nenhum"}
            
        elif new_type == "Tempo (Hora)":
            f = ctk.CTkFrame(self.input_container, fg_color="transparent")
            f.grid(row=0, column=0, sticky="e")
            
            time_ent = ctk.CTkEntry(f, placeholder_text="14:30", width=80, height=38)
            time_ent.grid(row=0, column=0, sticky="w", padx=(0, 10))
            
            format_var = ctk.StringVar(value="HH:MM")
            format_menu = ctk.CTkOptionMenu(f, variable=format_var, width=120,
                values=["HH:MM", "HH:MM:SS", "Formato '14h 30m'"])
            format_menu.grid(row=0, column=1, sticky="w")
            
            if preload_data:
                if preload_data.get("raw_time"): time_ent.insert(0, preload_data["raw_time"])
                if preload_data.get("format"): format_var.set(preload_data["format"])
                
            def get_time_val():
                raw_t = time_ent.get()
                fmt = format_var.get()
                if fmt == "Formato '14h 30m'" and ":" in raw_t:
                    parts = raw_t.split(":")
                    if len(parts) >= 2: return f"{parts[0]}h {parts[1]}m"
                return raw_t
                
            self.current_value_getter = lambda: {"type": "texto", "value": get_time_val()}
            self.current_state_getter = lambda: {"ui_type": new_type, "raw_time": time_ent.get(), "format": format_var.get()}
            
        elif new_type in ["Data", "Data e Hora"]:
            f = ctk.CTkFrame(self.input_container, fg_color="transparent")
            f.grid(row=0, column=0, sticky="e")
            
            date_ent = DateEntry(f, width=12, background='#1f538d',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', font=('Arial', 12))
            date_ent.grid(row=0, column=0, sticky="w", padx=(0, 10))
            
            time_ent = None
            col_idx = 1
            if new_type == "Data e Hora":
                time_ent = ctk.CTkEntry(f, placeholder_text="HH:MM", width=70, height=35)
                time_ent.grid(row=0, column=col_idx, sticky="w", padx=(0, 10))
                col_idx += 1
            
            format_var = ctk.StringVar(value="DD/MM/AAAA")
            if new_type == "Data":
                opts = ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD", "Por Extenso"]
            else:
                opts = ["DD/MM/AAAA às HH:MM", "AAAA-MM-DD HH:MM:SS", "Extenso"]
            
            format_menu = ctk.CTkOptionMenu(f, variable=format_var, values=opts, width=150)
            format_menu.grid(row=0, column=col_idx, sticky="w")
            
            if preload_data:
                if preload_data.get("raw_date"): 
                    try:
                        date_obj = datetime.strptime(preload_data["raw_date"], "%Y-%m-%d").date()
                        date_ent.set_date(date_obj)
                    except: pass
                if time_ent and preload_data.get("raw_time"):
                    time_ent.insert(0, preload_data["raw_time"])
                if preload_data.get("format"):
                    format_var.set(preload_data["format"])
            
            def get_datetime_val():
                d_obj = date_ent.get_date()
                fmt = format_var.get()
                t_str = time_ent.get() if time_ent else ""
                months = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                res = ""
                if fmt == "DD/MM/AAAA": res = d_obj.strftime("%d/%m/%Y")
                elif fmt == "MM/DD/AAAA": res = d_obj.strftime("%m/%d/%Y")
                elif fmt.startswith("AAAA-MM-DD"): res = d_obj.strftime("%Y-%m-%d")
                elif fmt.startswith("Por Extenso") or fmt.startswith("Extenso"):
                    res = f"{d_obj.day:02d} de {months[d_obj.month]} de {d_obj.year}"
                if time_ent and t_str:
                    if "HH:MM:SS" in fmt: res += f" {t_str}:00"
                    elif "às" in fmt or "Extenso" in fmt: res += f" às {t_str}"
                    else: res += f" {t_str}"
                return {"type": "texto", "value": res}
                
            self.current_value_getter = get_datetime_val
            self.current_state_getter = lambda: {
                "ui_type": new_type,
                "raw_date": date_ent.get_date().strftime("%Y-%m-%d"),
                "raw_time": time_ent.get() if time_ent else "",
                "format": format_var.get()
            }
            
        elif new_type == "Imagem":
            f = ctk.CTkFrame(self.input_container, fg_color="transparent")
            f.grid(row=0, column=0, sticky="e")
            
            # Signature Library Option
            lib_btn = ctk.CTkButton(f, text="📚 Biblioteca", width=100, height=35, command=self.pick_from_library)
            lib_btn.grid(row=0, column=0, sticky="w", padx=(0, 10))
            
            btn = ctk.CTkButton(f, text="Selecionar Arquivo", command=self.pick_image, height=35, width=150)
            btn.grid(row=0, column=1, sticky="w")
            
            self.img_lbl = ctk.CTkLabel(f, text="...", text_color="gray50", width=120)
            self.img_lbl.grid(row=0, column=2, sticky="w", padx=10)
            
            if self.selected_image_path and os.path.exists(self.selected_image_path):
                self.img_lbl.configure(text=f"{os.path.basename(self.selected_image_path)[:12]}...")
                
            self.current_value_getter = lambda: {"type": "imagem", "value": self.selected_image_path}
            self.current_state_getter = lambda: {"ui_type": new_type, "raw_val": self.selected_image_path}
            
    def pick_from_library(self):
        imgs = database.get_library_images()
        if not imgs:
            messagebox.showinfo("Vazio", "Nenhuma imagem cadastrada na biblioteca.")
            return
            
        # Quick picker (simple Toplevel)
        picker = ctk.CTkToplevel(self)
        picker.title("Escolher da Biblioteca")
        picker.geometry("300x400")
        picker.attributes('-topmost', True)
        
        frame = ctk.CTkScrollableFrame(picker)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i_data in imgs:
            _, name, path = i_data
            btn = ctk.CTkButton(frame, text=name, command=lambda p=path, pk=picker: self._select_lib_img(p, pk))
            btn.pack(fill="x", pady=5)
            
    def _select_lib_img(self, path, picker):
        self.selected_image_path = path
        self.img_lbl.configure(text=f"{os.path.basename(path)[:12]}...")
        picker.destroy()

    def pick_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filepath:
            self.selected_image_path = filepath
            filename = os.path.basename(filepath)
            self.img_lbl.configure(text=f"{filename[:12]}...")
            
    def get_value(self):
        return self.current_value_getter()
        
    def get_ui_state(self):
        return self.current_state_getter()


class DocumentGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.templates = []
        self.selected_template_id = None
        self.selected_template_path = None
        self.variables = []
        self.variable_rows = {}
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Gerar Documento", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(self.header_frame, text="Automação completa: individual, em lote e exportação PDF.", text_color="gray60")
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))
        
        # Selection Box + Actions
        self.top_box = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=0)
        self.top_box.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.top_box.grid_columnconfigure(1, weight=1)
        
        lbl_select = ctk.CTkLabel(self.top_box, text="Modelo Base:", font=ctk.CTkFont(weight="bold"))
        lbl_select.grid(row=0, column=0, padx=20, pady=15)
        
        self.template_var = ctk.StringVar(value="Escolher...")
        self.combobox = ctk.CTkOptionMenu(self.top_box, variable=self.template_var, command=self.on_template_select, width=300, height=38)
        self.combobox.grid(row=0, column=1, padx=10, pady=15, sticky="w")
        
        # Bulk Option
        self.bulk_btn = ctk.CTkButton(self.top_box, text="⚡ Geração em Lote (Excel)", command=self.bulk_generation_ui, 
                                       fg_color="#28a745", hover_color="#218838", height=38, corner_radius=0)
        self.bulk_btn.grid(row=0, column=2, padx=10, pady=15)
        
        self.backup_btn = ctk.CTkButton(self.top_box, text="🛡️ Backup", command=self.do_backup, width=100, height=38, corner_radius=0)
        self.backup_btn.grid(row=0, column=3, padx=10, pady=15)
        
        # Progress Bar Area
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=20)
        self.progress_frame.grid_remove() # Hidden by default
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.progress_lbl = ctk.CTkLabel(self.progress_frame, text="Processando...", font=ctk.CTkFont(size=12))
        self.progress_lbl.pack()
        
        # Form Box
        self.gen_box = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=0)
        self.gen_box.grid(row=3, column=0, sticky="nsew")
        self.gen_box.grid_rowconfigure(1, weight=1)
        self.gen_box.grid_columnconfigure(0, weight=1)
        
        box_hdr = ctk.CTkFrame(self.gen_box, fg_color="transparent")
        box_hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        box_title = ctk.CTkLabel(box_hdr, text="Configuração das Chaves", font=ctk.CTkFont(size=18, weight="bold"))
        box_title.pack(side="left")
        
        self.pdf_var = ctk.BooleanVar(value=False)
        self.pdf_check = ctk.CTkCheckBox(box_hdr, text="Exportar também para PDF", variable=self.pdf_var)
        self.pdf_check.pack(side="right")
        
        self.form_frame = ctk.CTkScrollableFrame(self.gen_box, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        self.generate_btn = ctk.CTkButton(self.gen_box, text="Gerar Documento Final", command=self.generate_document, 
                                          state="disabled", height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.generate_btn.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        self.load_combobox()

    def do_backup(self):
        folder = filedialog.askdirectory(title="Selecionar Pasta para Backup")
        if folder:
            path = database.perform_backup(folder)
            messagebox.showinfo("Sucesso", f"Backup gerado em:\n{path}")

    def load_combobox(self):
        self.templates = database.get_templates()
        if not self.templates:
            self.combobox.configure(values=["Nenhum cadastrado"])
        else:
            values = [t[1] for t in self.templates]
            self.combobox.configure(values=values)
            
    def on_template_select(self, choice):
        for widget in self.form_frame.winfo_children(): widget.destroy()
        self.variable_rows.clear()
        self.variables.clear()
        
        selected = next((t for t in self.templates if t[1] == choice), None)
        if selected:
            self.selected_template_id = selected[0]
            self.selected_template_path = selected[2]
            
            self.gen_box.grid_remove()
            self.progress_frame.grid()
            self.progress_bar.set(0)
            self.update()
            
            for i in range(1, 11):
                time.sleep(0.04)
                self.progress_bar.set(i/10)
                self.update()
            
            cache_data = database.get_template_cache(self.selected_template_id)
            
            try:
                raw_vars = docx_parser.extract_variables(self.selected_template_path)
                self.variables = sorted(raw_vars)
                
                if not self.variables:
                    lbl = ctk.CTkLabel(self.form_frame, text="Nenhuma variável {id} encontrada.")
                    lbl.grid(row=0, column=0, padx=10, pady=10)
                else:
                    for i, var in enumerate(self.variables):
                        preload = cache_data.get(var, None)
                        row = VariableInputRow(self.form_frame, var, preload_data=preload)
                        row.grid(row=i, column=0, sticky="ew", pady=2)
                        self.variable_rows[var] = row
                
                self.generate_btn.configure(state="normal")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na leitura: {e}")
            
            self.progress_frame.grid_remove()
            self.gen_box.grid()
                
    def generate_document(self):
        if not self.selected_template_path: return
        data = {}
        cache_state = {}
        for var, row in self.variable_rows.items():
            data[var] = row.get_value()
            cache_state[var] = row.get_ui_state()
            
        save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word", "*.docx")])
        if save_path:
            try:
                database.save_template_cache(self.selected_template_id, cache_state)
                docx_parser.generate_document(self.selected_template_path, save_path, data, convert_to_pdf=self.pdf_var.get())
                messagebox.showinfo("Sucesso", "Concluído!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

    def bulk_generation_ui(self):
        if not self.selected_template_path:
            messagebox.showwarning("Aviso", "Selecione um modelo primeiro.")
            return
            
        file_path = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv")])
        if not file_path: return
        
        try:
            if file_path.endswith('.csv'): df = pd.read_csv(file_path)
            else: df = pd.read_excel(file_path)
            
            # Simple column mapping logic (must match {var_name})
            cols = df.columns.tolist()
            missing = [v for v in self.variables if v not in cols]
            
            if missing:
                if not messagebox.askyesno("Mapeamento", f"As variáveis {missing} não foram encontradas nas colunas do Excel. Deseja ignorar e gerar com campos vazios?"):
                    return
            
            dest_dir = filedialog.askdirectory(title="Onde salvar os documentos?")
            if not dest_dir: return
            
            # Start process
            self.gen_box.grid_remove()
            self.progress_frame.grid()
            total = len(df)
            
            for index, row in df.iterrows():
                self.progress_lbl.configure(text=f"Processando linha {index+1}/{total}...")
                self.progress_bar.set((index+1)/total)
                self.update()
                
                # Build data dict for docx_parser
                row_data = {}
                for var in self.variables:
                    val = row.get(var, "")
                    row_data[var] = {"type": "texto", "value": str(val)}
                
                filename = f"Doc_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                out_path = os.path.join(dest_dir, filename)
                docx_parser.generate_document(self.selected_template_path, out_path, row_data, convert_to_pdf=self.pdf_var.get())
            
            messagebox.showinfo("Sucesso", f"{total} documentos gerados com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro no Lote", f"Falha: {e}")
        finally:
            self.progress_frame.grid_remove()
            self.gen_box.grid()
