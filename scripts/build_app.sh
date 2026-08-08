#!/usr/bin/env bash
# Compila o Jarvis numa app de ambiente de trabalho (Linux/macOS).
set -e
cd "$(dirname "$0")/.."

echo "==> A instalar dependências de build…"
pip install ".[build]"

echo "==> A empacotar com PyInstaller…"
pyinstaller packaging/jarvis.spec --noconfirm

echo ""
echo "✅ Pronto! A app está em: dist/Jarvis"
echo "   Executa com: ./dist/Jarvis"
