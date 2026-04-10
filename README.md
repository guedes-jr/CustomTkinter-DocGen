# DocGen Pro v2.0 - Automação Profissional de Documentos

<div align="center">
  <img src="assets/screenshots/login.png" width="45%" />
  <img src="assets/screenshots/dashboard.png" width="45%" />
</div>

O **DocGen Pro** é um software desktop de alta performance desenvolvido em Python para automação completa de documentos Word (`.docx`) e PDF. Ideal para departamentos jurídicos, administrativos e comerciais que lidam com fluxos repetitivos de contratos, declarações e relatórios.

![Status](https://img.shields.io/badge/Status-v2.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-yellow?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)

---

## 🌟 Novidades v2.0

###Banco de Dados Flexível
- **Múltiplos Bancos**: Escolha qualquer arquivo `.db` ou `.sqlite` como banco de dados
- **Rede Compartilhada**: Sistema de lock para múltiplos usuários em pasta compartilhada (Dropbox, OneDrive, Google Drive)
- **Configuração via Interface**: Nouvelle tela de configurações para selecionar o arquivo

###Sistema de Permissões
- **3 Grupos de Usuários**:
  - `admin` - Acesso completo
  - `manager` - Gerencia usuários e configurações (não pode criar admin)
  - `user` - Apenas geração de documentos

###Melhorias na Geração
- **Nome Personalizado**: Escolha variáveis do Excel/planilha para nomear os arquivos
- **Planilha Modelo**: Baixe um modelo Excel com as variáveis do documento Word
- **Anti-Colisão**: Números sequenciais e sufixos para evitar arquivos duplicados
- **Configuração de Nome Individual**: Mesmo recurso para geração individual

---

## 🌟 Funcionalidades

- **Geração em Lote**: Importe planilhas Excel/CSV e gere centenas de documentos
- **Exportação PDF Integrada**: Conversão nativa via Mammoth + xhtml2pdf
- **Biblioteca de Ativos**: Gerencie assinaturas e logotipos
- **Máscaras de Entrada**: CPF, CNPJ, Datas, Moeda
- **Dicionário de Variáveis**: Descrições/tooltips para cada campo
- **Tema Dark/Light**: Persistência de preferência
- **Tela Chegada**: Inicia maximizado

---

## 🛠 Tecnologias

- **Python 3.13** + **CustomTkinter**
- **SQLite** (com lock para multi-acesso)
- **pandas** (processamento Excel/CSV)
- **python-docx** + **mammoth** + **xhtml2pdf**

---

## 📥 Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

**Login padrão**: `admin` / `admin`

---

## 📁 Estrutura

```
├── main.py                     # Entry point
├── database.py                # SQLite + lock multi-usuário
├── requirements.txt            # Dependências
├── gui/
│   ├── login.py               # Tela de login
│   ├── dashboard.py           # Menu principal
│   ├── document_generator.py  # Geração individual/lote
│   ├── template_manager.py   # Gerenciar modelos .docx
│   ├── image_library.py       # Biblioteca de imagens
│   ├── user_management.py     # Gestão de usuários
│   └── settings.py            # Configurações do banco
├── utils/
│   └── docx_parser.py         # Injeção Word + PDF
└── assets/                    # Imagens
```

---

## 📂 Uso

### 1. Modelos Word
Use variáveis no formato `{nome_variavel}` no seu documento:
```
Prezado {nome_cliente},
Data: {data_vencimento}
```

### 2. Gerar Documento
- **Individual**: Preencha os campos e gere
- **Lote**: Use Excel com colunas matching as variáveis
- **Nome do Arquivo**: Escolha variáveis para compor o nome

### 3. Planilha Modelo
Em "Gerenciar Modelos", clique em "📥 Planilha" para baixar modelo Excel com as variáveis do documento.

---

## 🔒 Sistema de Lock

O sistema usa arquivo `database.lock` para evitar conflitos em uso simultâneo:
- Timeout de 5 minutos para locks órfãos
- Validação automática antes de operações de escrita
- Mensagem clara se banco estiver em uso

---

## 🤖 Configuração de IA

Arquivos `.ai-*` na raiz otimizam desenvolvimento com IA:
- `.ai-ignore` - Ignora arquivos irrelevantes
- `.ai-context` - Contexto do projeto
- `.ai-system` - Regras de comportamento

---

## 🛡️ Licença
Uso interno. Todos os direitos reservados.