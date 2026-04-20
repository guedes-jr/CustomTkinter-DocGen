# Makefile para o DocGen Pro

PYTHON = venv/bin/python
PIP = venv/bin/pip

.PHONY: help install run clean backup requirements build

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Criar venv e instalar dependências"
	@echo "  make run          - Executar o aplicativo"
	@echo "  make clean        - Remover arquivos temporários e caches"
	@echo "  make backup       - (Simulado) Dica de backup"
	@echo "  make requirements - Atualizar o arquivo requirements.txt"
	@echo "  make build        - Gerar o executável (instalador) para Windows"

install:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "\nInstalação concluída com sucesso! Use 'make run' para iniciar."

run:
	$(PYTHON) main.py

clean:
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	@echo "Limpeza concluída."

backup:
	@echo "Para backup manual, copie o arquivo 'database.db' e a pasta 'assets'."
	@echo "Lembre-se de que o sistema v1.0 possui um botão de backup interno."

requirements:
	$(PIP) freeze > requirements.txt
	@echo "requirements.txt atualizado."

build:
	rm -rf build/ dist/ "DocGen Pro.spec"
	$(PIP) install pyinstaller
	python -m PyInstaller --onefile --noconsole --icon "assets\icon.ico" --name "DocGen Pro" --add-data "assets;assets" --collect-all customtkinter --collect-all reportlab --collect-all xhtml2pdf main.py
	@echo "Executável Windows gerado com sucesso na pasta 'dist/DocGen Pro.exe'"
