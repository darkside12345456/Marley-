@echo off
REM Compila o Jarvis numa app de ambiente de trabalho (Windows).
cd /d "%~dp0.."

echo ==^> A instalar dependencias de build...
pip install ".[build]"

echo ==^> A empacotar com PyInstaller...
pyinstaller packaging\jarvis.spec --noconfirm

echo.
echo Pronto! A app esta em: dist\Jarvis.exe
pause
