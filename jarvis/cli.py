"""Ponto de entrada do Jarvis.

Uso:
    python -m jarvis            # abre o HUD holográfico no browser (recomendado)
    python -m jarvis web        # idem
    python -m jarvis voz        # conversa por voz no terminal
    python -m jarvis texto      # conversa por texto no terminal
    python -m jarvis "olá"      # pergunta única e sai
"""
from __future__ import annotations

import sys
import webbrowser

from .assistant import Assistant
from .config import config


def _executar_acoes(assistant: Assistant) -> None:
    """Executa ações de UI no terminal (abrir páginas; modelos 3D só no HUD web)."""
    for acao in assistant.last_actions:
        if acao.get("tipo") == "abrir_pagina":
            try:
                webbrowser.open(acao["url"])
            except Exception:
                print(f"   (abre manualmente: {acao['url']})")
        elif acao.get("tipo") == "modelo":
            print(f"   [Holo-Lab 3D disponível no HUD web: peça '{acao.get('peca')}']")
        elif acao.get("tipo") == "confirmar_comando":
            from .tools import system as system_mod

            print(f"\n   ⚠️  A Sonny quer executar: {acao.get('comando')}")
            try:
                resp = input("   Confirmar? (s/N) ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                resp = "n"
            if resp in {"s", "sim", "y"}:
                res = system_mod.run_command(acao.get("comando", ""), True)
                print(f"   {res.get('saida') or res.get('erro') or '(sem saída)'}")
            else:
                print("   Comando cancelado.")


def _banner() -> None:
    nome = config.name.upper()
    barra = "═" * (len(nome) + 8)
    print("\n".join([
        "",
        f"   ╔{barra}╗",
        f"   ║    {nome}    ║",
        f"   ╚{barra}╝",
        f"   modelo: {config.model}   ·   {config.ollama_host}",
        "",
    ]))


def run_web() -> None:
    from .web.server import run

    url = f"http://{config.host}:{config.port}"
    print(f"🌐 HUD do Jarvis em {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    run()


def run_text() -> None:
    _banner()
    assistant = Assistant(config)
    if not assistant.brain.is_available():
        print("⚠️  Ollama não está a responder. Corre 'ollama serve' e "
              f"'ollama pull {config.model}'.\n")
    print("Escreve 'sair' para terminar.\n")
    try:
        while True:
            texto = input("👤 > ").strip()
            if texto.lower() in {"sair", "exit", "quit"}:
                break
            if not texto:
                continue
            print("🤖 …a pensar")
            print(f"🤖 {assistant.ask(texto)}\n")
            _executar_acoes(assistant)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        assistant.close()
        print("\nAté já!")


def run_voice() -> None:
    _banner()
    from .voice import Voice

    assistant = Assistant(config)
    voice = Voice(config.language)
    if not voice.can_listen:
        print("ℹ️  Microfone/STT indisponível — vou usar o teclado. "
              "(instala com: pip install -r requirements-voz.txt)\n")
    voice.say("Sistemas online. Em que posso ajudar?")
    try:
        while True:
            texto = voice.listen()
            if not texto:
                continue
            if texto.lower().strip(" .!") in {"sair", "adeus", "desliga"}:
                voice.say("Até já!")
                break
            voice.say(assistant.ask(texto))
            _executar_acoes(assistant)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        assistant.close()


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0].lower() if argv else "web"

    if cmd in {"web", "hud"}:
        run_web()
    elif cmd in {"voz", "voice"}:
        run_voice()
    elif cmd in {"texto", "text", "chat"}:
        run_text()
    else:
        # Pergunta única
        from .brain import OllamaError

        assistant = Assistant(config)
        try:
            print(assistant.ask(" ".join(argv)))
        except OllamaError as exc:
            print(f"⚠️  {exc}")
        finally:
            assistant.close()


if __name__ == "__main__":
    main()
