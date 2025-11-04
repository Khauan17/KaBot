@echo off
rem Garante que o script execute a partir do seu próprio diretório
cd /d "%~dp0"

echo --- Verificando ambiente e iniciando o KaBot ---
echo.
echo Diretorio de trabalho atual:
cd

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Iniciando o script Python (main.py)...
python main.py

echo.
echo --- O bot foi desligado. ---
pause