"""Interface com o Ollama (modelo local).

Usa apenas a biblioteca padrão (urllib) para não obrigar a instalar nada.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Iterator


class OllamaError(RuntimeError):
    pass


class Brain:
    def __init__(self, host: str, model: str, temperature: float = 0.7):
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature

    def _post(self, path: str, payload: dict, stream: bool = False):
        url = f"{self.host}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            return urllib.request.urlopen(req, timeout=120)
        except urllib.error.URLError as exc:
            raise OllamaError(
                f"Não consegui contactar o Ollama em {self.host}. "
                "Está a correr? Instala em https://ollama.com e corre 'ollama serve'. "
                f"(detalhe: {exc})"
            ) from exc

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Uma volta de chat (não-streaming). Devolve a mensagem do assistente."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if tools:
            payload["tools"] = tools
        resp = self._post("/api/chat", payload)
        body = json.loads(resp.read().decode("utf-8"))
        if "error" in body:
            raise OllamaError(body["error"])
        return body.get("message", {})

    def stream(self, messages: list[dict]) -> Iterator[str]:
        """Gera a resposta token a token (para o HUD falar em tempo real)."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": self.temperature},
        }
        resp = self._post("/api/chat", payload, stream=True)
        for raw in resp:
            raw = raw.strip()
            if not raw:
                continue
            chunk = json.loads(raw.decode("utf-8"))
            piece = chunk.get("message", {}).get("content", "")
            if piece:
                yield piece
            if chunk.get("done"):
                break

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False
