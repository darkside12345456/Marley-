"""Servidor web do HUD holográfico do Jarvis.

Serve a interface e expõe um endpoint /api/chat que responde em streaming
(Server-Sent Events) para o orbe reagir e a voz do browser falar em tempo real.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    from flask import Flask, Response, jsonify, request, send_from_directory
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Falta o Flask. Instala com: pip install -r requirements.txt"
    ) from exc

from ..assistant import Assistant
from ..config import WORKSPACE_DIR, config

STATIC = Path(__file__).parent / "static"


def create_app(assistant: Assistant | None = None) -> Flask:
    assistant = assistant or Assistant(config)
    app = Flask(__name__, static_folder=None)

    @app.route("/")
    def index():
        return send_from_directory(STATIC, "index.html")

    @app.route("/static/<path:name>")
    def static_files(name):
        return send_from_directory(STATIC, name)

    @app.route("/workspace/<path:name>")
    def workspace_files(name):
        # Serve as apps criadas pelo Jarvis. Restrito à sandbox workspace/.
        base = WORKSPACE_DIR.resolve()
        alvo = (base / name).resolve()
        if not str(alvo).startswith(str(base)) or not alvo.is_file():
            return ("Não encontrado", 404)
        return send_from_directory(base, str(alvo.relative_to(base)))

    @app.route("/api/status")
    def status():
        return jsonify(
            {
                "nome": config.name,
                "modelo": config.model,
                "ollama_ativo": assistant.brain.is_available(),
            }
        )

    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json(force=True)
        texto = (data.get("texto") or "").strip()
        if not texto:
            return jsonify({"erro": "texto vazio"}), 400

        def gen():
            try:
                resposta = assistant.ask(texto)
            except Exception as exc:  # noqa: BLE001
                yield f"data: {json.dumps({'erro': str(exc)})}\n\n"
                return
            # Envia a resposta e as ações (abrir página, projetar modelo 3D…).
            payload = {"resposta": resposta, "acoes": assistant.last_actions}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(gen(), mimetype="text/event-stream")

    @app.route("/api/reset", methods=["POST"])
    def reset():
        assistant.reset()
        return jsonify({"ok": True})

    return app


def run(host: str | None = None, port: int | None = None) -> None:
    app = create_app()
    app.run(host=host or config.host, port=port or config.port, threaded=True)


if __name__ == "__main__":
    run()
