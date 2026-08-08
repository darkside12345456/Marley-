"""Ponto de entrada para a app de ambiente de trabalho (PyInstaller).

Arranca o servidor do HUD e abre o browser. É este ficheiro que o PyInstaller
empacota (ver packaging/jarvis.spec).
"""
from jarvis.cli import run_web

if __name__ == "__main__":
    run_web()
