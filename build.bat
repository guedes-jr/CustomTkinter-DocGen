@echo off
echo ===================================================
echo   Gerando o Executavel do DocGen Pro (Windows)
echo ===================================================
echo.
echo Limpando arquivos de builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "DocGen Pro.spec" del /q "DocGen Pro.spec"

echo.
echo Garantindo instalacao do PyInstaller no ambiente atual...
pip install pyinstaller -q

echo.
echo Compilando... aguarde isso pode levar alguns minutos.

python -m PyInstaller --onefile --noconsole --icon "assets\icon.ico" --name "DocGen Pro" --add-data "assets;assets" --collect-all customtkinter --collect-all reportlab --collect-all xhtml2pdf main.py

echo.
if exist "dist\DocGen Pro.exe" (
    echo ===================================================
    echo [SUCESSO] O seu executavel foi gerado na pasta:
    echo dist\DocGen Pro.exe
    echo ===================================================
) else (
    echo ===================================================
    echo [ERRO] Ocorreu um problema ao compilar o executavel.
    echo ===================================================
)
pause
