"""Execução de comandos do sistema — desativada por omissão (ver config)."""
from __future__ import annotations

import subprocess


def run_command(comando: str, allow_shell: bool = False) -> dict:
    if not allow_shell:
        return {
            "erro": "Comandos do sistema estão desativados.",
            "como_ativar": "Define JARVIS_ALLOW_SHELL=1 no ficheiro .env para permitir.",
        }
    try:
        proc = subprocess.run(
            comando, shell=True, capture_output=True, text=True, timeout=30
        )
        return {
            "comando": comando,
            "codigo": proc.returncode,
            "saida": (proc.stdout or "")[:4000],
            "erro": (proc.stderr or "")[:2000],
        }
    except subprocess.TimeoutExpired:
        return {"erro": "O comando demorou demasiado (timeout de 30s)."}
