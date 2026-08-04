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


def _banner() -> None:
    print("\n".join([
        "",
        "   ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗",
        "   ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝",
        "   ██║███████║██████╔╝██║   ██║██║███████╗",
        "██╗██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║",
        "╚████║██║  ██║██║  ██║ ╚████╔╝ ██║███████║",
        " ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝",
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
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        assistant.close()
        print("\nAté já, senhor.")


def run_voice() -> None:
    _banner()
    from .voice import Voice

    assistant = Assistant(config)
    voice = Voice(config.language)
    if not voice.can_listen:
        print("ℹ️  Microfone/STT indisponível — vou usar o teclado. "
              "(instala com: pip install -r requirements-voz.txt)\n")
    voice.say("Sistemas online. Em que posso ajudar, senhor?")
    try:
        while True:
            texto = voice.listen()
            if not texto:
                continue
            if texto.lower().strip(" .!") in {"sair", "adeus", "desliga"}:
                voice.say("Até já, senhor.")
                break
            voice.say(assistant.ask(texto))
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
        assistant = Assistant(config)
        print(assistant.ask(" ".join(argv)))
        assistant.close()


if __name__ == "__main__":
    main()
