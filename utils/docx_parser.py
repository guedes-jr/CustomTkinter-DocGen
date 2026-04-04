from docx import Document
from docx.shared import Cm
import re
import os
import mammoth
from xhtml2pdf import pisa
import platform

def extract_variables(docx_path):
    doc = Document(docx_path)
    variables = set()
    pattern = r'\{([a-zA-Z0-9_]+)\}'
    
    for para in doc.paragraphs:
        matches = re.findall(pattern, para.text)
        for m in matches: variables.add(m)
            
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                matches = re.findall(pattern, cell.text)
                for m in matches: variables.add(m)
                    
    return list(variables)

def generate_document(template_path, output_path, data, convert_to_pdf=False):
    doc = Document(template_path)
    
    # Replace variables in paragraphs
    for para in doc.paragraphs:
        _replace_in_element(para, data)
            
    # Replace variables in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    _replace_in_element(para, data)
                
    doc.save(output_path)
    
    if convert_to_pdf:
        try:
            pdf_path = output_path.replace('.docx', '.pdf')
            
            # 1. Converter Word (.docx) para HTML usando Mammoth
            with open(output_path, "rb") as docx_file:
                # O Mammoth gera um HTML limpo e incorpora imagens como base64
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value
                
                # Adicionar um estilo básico para o PDF (Margens e Fontes)
                styled_html = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @page {{
                            size: a4;
                            margin: 2.5cm;
                        }}
                        body {{
                            font-family: Arial, sans-serif;
                            font-size: 11pt;
                            line-height: 1.5;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                        }}
                        th, td {{
                            border: 1px solid #ccc;
                            padding: 8px;
                            text-align: left;
                        }}
                        img {{
                            max-width: 100%;
                            height: auto;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # 2. Converter HTML para PDF usando xhtml2pdf (Pure Python)
                with open(pdf_path, "wb") as pdf_file:
                    pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)
                    
                if pisa_status.err:
                    raise Exception("Erro interno na geração do PDF (xhtml2pdf).")
                
            return pdf_path
        except Exception as e:
            raise Exception(f"Falha na conversão de PDF independente: {e}")
            
    return output_path

def _replace_in_element(para, data):
    pattern = r'\{([a-zA-Z0-9_]+)\}'
    total_text = para.text
    matches = re.findall(pattern, total_text)
    
    if not matches: return

    for key in matches:
        if key in data:
            entry = data[key]
            val = entry.get("value", "")
            
            if entry.get("type") == "imagem":
                if val and os.path.exists(val):
                    para.text = para.text.replace(f"{{{key}}}", "")
                    run = para.add_run()
                    run.add_picture(val, width=Cm(5))
            else:
                para.text = para.text.replace(f"{{{key}}}", str(val))
