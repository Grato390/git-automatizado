@echo off
echo ========================================
echo   CREANDO ARCHIVO .EXE
echo ========================================
echo.

cd /d "%~dp0"
echo [1/4] Cambiando al directorio del proyecto...
echo Directorio: %CD%
echo.

echo [2/4] Activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✓ Entorno virtual activado
) else (
    echo ✗ ERROR: No se encuentra el entorno virtual
    echo Creando entorno virtual...
    py -m venv venv
    call venv\Scripts\activate.bat
    echo ✓ Entorno virtual creado
)
echo.

echo [3/4] Instalando PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ✗ ERROR al instalar PyInstaller
    pause
    exit /b 1
)
echo ✓ PyInstaller instalado
echo.

echo [4/4] Creando archivo .exe (esto puede tardar 1-2 minutos)...
echo Por favor espera...
echo.

if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

pyinstaller --onefile --windowed --name "Git-Automation" --clean git_automation_gui.py

if errorlevel 1 (
    echo.
    echo ✗ ERROR al crear el .exe
    echo Revisa los mensajes de error arriba
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ¡COMPLETADO EXITOSAMENTE!
echo ========================================
echo.
if exist "dist\Git-Automation.exe" (
    echo ✓ Archivo creado: dist\Git-Automation.exe
    echo.
    echo Puedes copiar ese .exe a cualquier lugar y ejecutarlo directamente.
) else (
    echo ✗ ERROR: El archivo .exe no se creó correctamente
    echo Revisa los mensajes de error arriba
)
echo.
pause
