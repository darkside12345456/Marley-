"""Assistente de configuração do Ollama (o cérebro da Sonny).

Corre:  python -m jarvis setup     (ou  jarvis setup)

Verifica se o Ollama está instalado, a correr e com o modelo pronto — e, se
faltar o modelo, oferece-se para o descarregar. O Ollama corre localmente no
teu computador; este assistente apenas te guia e trata do 'ollama pull'.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request

from .config import config

INSTALL_URL = "https://ollama.com/download"


def _modelos_instalados() -> list[str] | None:
    try:
        req = urllib.request.Request(f"{config.ollama_host}/api/tags")
        data = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return None


def _tem_modelo(instalados: list[str], modelo: str) -> bool:
    base = modelo.split(":")[0]
    return any(m == modelo or m.split(":")[0] == base for m in instalados)


def run_setup() -> None:
    print("\n🧠  Configuração do cérebro da Sonny (Ollama)\n" + "─" * 44)
    print(f"   Servidor:  {config.ollama_host}")
    print(f"   Modelo:    {config.model}\n")

    tem_binario = shutil.which("ollama") is not None
    from .brain import Brain
    brain = Brain(config.ollama_host, config.model, config.temperature)
    servidor_ativo = brain.is_available()

    # 1) Ollama instalado?
    if not tem_binario and not servidor_ativo:
        print("❌  O Ollama não parece estar instalado.")
        print(f"    → Instala-o em: {INSTALL_URL}")
        print("      (Linux/macOS pode ser:  curl -fsSL https://ollama.com/install.sh | sh )")
        print("\n    Depois de instalar, corre outra vez:  jarvis setup\n")
        return
    print("✅  Ollama encontrado.")

    # 2) Servidor a correr?
    if not servidor_ativo:
        print("⚠️   O servidor do Ollama não está a responder.")
        print("    → Abre um terminal e corre:  ollama serve")
        print("      (Em Windows/macOS costuma arrancar sozinho com a app.)")
        print("\n    Depois, corre outra vez:  jarvis setup\n")
        return
    print("✅  Servidor do Ollama a responder.")

    # 3) Modelo pronto?
    instalados = _modelos_instalados() or []
    if _tem_modelo(instalados, config.model):
        print(f"✅  Modelo '{config.model}' pronto a usar.\n")
        print("🎉  Tudo a postos! Arranca a Sonny com:  jarvis\n")
        return

    print(f"ℹ️   O modelo '{config.model}' ainda não está descarregado.")
    if instalados:
        print("    Modelos que já tens:  " + ", ".join(instalados))
    try:
        resp = input(f"\n    Queres que eu descarregue '{config.model}' agora? (s/N) ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        resp = "n"
    if resp not in {"s", "sim", "y"}:
        print(f"\n    Sem problema. Podes fazê-lo tu com:  ollama pull {config.model}\n")
        return

    print(f"\n⬇️   A descarregar '{config.model}' (pode demorar uns minutos)…\n")
    try:
        subprocess.run(["ollama", "pull", config.model], check=True)
        print(f"\n✅  Modelo '{config.model}' instalado!  Arranca com:  jarvis\n")
    except Exception as exc:  # noqa: BLE001
        print(f"\n❌  Falhou o download: {exc}")
        print(f"    Tenta manualmente:  ollama pull {config.model}\n")
