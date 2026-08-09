"""Ponto de entrada para a app de ambiente de trabalho.

Se o `pywebview` estiver instalado, abre o Jarvis numa **janela nativa**
(sem browser). Caso contrário, arranca o servidor e abre o browser.

É este ficheiro que o PyInstaller empacota (ver packaging/jarvis.spec).
"""
from __future__ import annotations

import threading

from jarvis.config import config

APP_NOME = "J.A.R.V.I.S."


def _iniciar_servidor() -> None:
    from jarvis.web.server import create_app

    app = create_app()
    app.run(host=config.host, port=config.port, threaded=True, use_reloader=False)


def main() -> None:
    try:
        import webview  # janela nativa (opcional)
    except Exception:
        # Sem pywebview: usa o browser.
        from jarvis.cli import run_web
        run_web()
        return

    # Arranca o Flask em segundo plano e mostra numa janela nativa.
    threading.Thread(target=_iniciar_servidor, daemon=True).start()
    webview.create_window(
        APP_NOME, f"http://{config.host}:{config.port}",
        width=1180, height=820, min_size=(900, 640),
    )
    webview.start()


if __name__ == "__main__":
    main()
