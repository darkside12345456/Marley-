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
from ..scheduler import get_scheduler
from ..scenes import get_store
from .. import mesh as mesh_mod

STATIC = Path(__file__).parent / "static"


def create_app(assistant: Assistant | None = None) -> Flask:
    assistant = assistant or Assistant(config)
    app = Flask(__name__, static_folder=None)

    # Arranca a verificação de segurança automática, se configurada.
    if config.security_interval and config.security_interval > 0:
        get_scheduler().iniciar(config.security_interval)

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

    @app.route("/api/security/last")
    def security_last():
        return jsonify(get_scheduler().estado())

    # --- Exportar um sólido fechado para .obj ---
    @app.route("/api/export/<forma>")
    def export_obj(forma):
        escala = float(request.args.get("escala", 1) or 1)
        segmentos = int(float(request.args.get("segmentos", 0) or 0))
        obj = mesh_mod.gerar_obj(forma, escala, segmentos)
        return Response(
            obj, mimetype="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{forma}.obj"'},
        )

    # --- Projetos 3D (guardar / carregar entre sessões) ---
    @app.route("/api/scene/current", methods=["POST"])
    def scene_current():
        data = request.get_json(force=True) or {}
        get_store().definir_atual(data.get("partes", []))
        return jsonify({"ok": True})

    @app.route("/api/scene/save", methods=["POST"])
    def scene_save():
        data = request.get_json(force=True) or {}
        return jsonify(get_store().guardar(
            data.get("nome", ""), data.get("partes"), data.get("thumb")))

    @app.route("/api/scene/list")
    def scene_list():
        return jsonify({"projetos": get_store().listar_detalhado()})

    @app.route("/api/scene/load")
    def scene_load():
        return jsonify(get_store().carregar(request.args.get("nome", "")))

    @app.route("/api/scene/thumb/<nome>")
    def scene_thumb(nome):
        caminho = get_store().caminho_thumb(nome)
        if not caminho:
            return ("Sem miniatura", 404)
        return send_from_directory(caminho.parent, caminho.name)

    @app.route("/api/scene/delete", methods=["POST"])
    def scene_delete():
        data = request.get_json(force=True) or {}
        return jsonify(get_store().apagar(data.get("nome", "")))

    @app.route("/api/scene/rename", methods=["POST"])
    def scene_rename():
        data = request.get_json(force=True) or {}
        return jsonify(get_store().renomear(data.get("nome", ""), data.get("novo", "")))

    return app


def run(host: str | None = None, port: int | None = None) -> None:
    app = create_app()
    app.run(host=host or config.host, port=port or config.port, threaded=True)


if __name__ == "__main__":
    run()
