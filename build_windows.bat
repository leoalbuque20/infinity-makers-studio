@echo off
:: Infinity Makers Studio — Empacotador Windows
echo.
echo ============================================
echo   Infinity Makers Studio — Build para .exe
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Instale em python.org
    pause
    exit /b 1
)

:: Instalar dependencias
echo [1/3] Instalando dependencias...
python -m pip install customtkinter Pillow pyinstaller --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

:: Localizar customtkinter
echo [2/3] Empacotando com PyInstaller...
for /f "delims=" %%i in ('python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i

:: Empacotar usando python -m pyinstaller (funciona mesmo sem pyinstaller no PATH)
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "InfinityMakersStudio" ^
    --add-data "%CTK_PATH%;customtkinter" ^
    infinity_makers_studio.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao empacotar.
    pause
    exit /b 1
)

echo [3/3] Pronto!
echo.
echo O executavel esta em: dist\InfinityMakersStudio.exe
echo.
pause
