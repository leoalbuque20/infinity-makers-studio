@echo off
:: Infinity Makers Studio — Empacotador Windows
:: Execute este arquivo para gerar o .exe na pasta dist\

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
pip install customtkinter pyinstaller Pillow --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

:: Empacotar
echo [2/3] Empacotando com PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "InfinityMakersStudio" ^
    --add-data "%LocalAppData%\Programs\Python\Python312\Lib\site-packages\customtkinter;customtkinter" ^
    infinity_makers_studio.py

if %ERRORLEVEL% NEQ 0 (
    :: Tentar caminho alternativo do customtkinter
    for /f "delims=" %%i in ('python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i
    pyinstaller ^
        --onefile ^
        --windowed ^
        --name "InfinityMakersStudio" ^
        --add-data "%CTK_PATH%;customtkinter" ^
        infinity_makers_studio.py
)

echo [3/3] Pronto!
echo.
echo O executavel esta em: dist\InfinityMakersStudio.exe
echo.
pause
