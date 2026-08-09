# -*- mode: python ; coding: utf-8 -*-
# Ficheiro de configuração do PyInstaller para empacotar o Jarvis como app.
#
# Uso:
#   pip install ".[build]"
#   pyinstaller packaging/jarvis.spec
#
# O resultado fica em dist/Jarvis (ou dist/Jarvis.exe no Windows).

import os

block_cipher = None

# Inclui os ficheiros estáticos do HUD (HTML/CSS/JS) no executável.
datas = [("../jarvis/web/static", "jarvis/web/static")]

a = Analysis(
    ["../run_desktop.py"],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=datas,
    hiddenimports=["flask", "jarvis", "jarvis.web.server"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Jarvis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,   # sem janela de terminal (app de ambiente de trabalho)
    icon="../assets/icon.ico",
)
