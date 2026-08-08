"""Guardar e carregar projetos do Holo-Lab (cenas 3D) entre sessões.

Guarda cada cena como um ficheiro JSON em data/scenes/. Mantém também a "cena
atual" (sincronizada pelo HUD) para que se possa guardar por voz.
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from .config import DATA_DIR
from .tools.holo import plan_scene

_DIR = DATA_DIR / "scenes"


def _guardar_thumb(slug: str, thumb: str | None) -> bool:
    """Guarda a miniatura (dataURL PNG) como ficheiro .png. Devolve True se ok."""
    if not thumb or "," not in thumb:
        return False
    try:
        dados = base64.b64decode(thumb.split(",", 1)[1])
        (_DIR / f"{slug}.png").write_bytes(dados)
        return True
    except Exception:
        return False


def _slug(nome: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", (nome or "cena").strip().lower()).strip("-")
    return s or "cena"


class SceneStore:
    def __init__(self) -> None:
        _DIR.mkdir(parents=True, exist_ok=True)
        self.atual: list[dict] = []

    def definir_atual(self, partes) -> None:
        self.atual = plan_scene(partes if isinstance(partes, list) else []).get("partes", [])

    def guardar(self, nome: str, partes=None, thumb: str | None = None) -> dict:
        dados = plan_scene(partes).get("partes", []) if partes is not None else self.atual
        if not dados:
            return {"erro": "não há nada para guardar (cena vazia)."}
        slug = _slug(nome)
        caminho = _DIR / f"{slug}.json"
        caminho.write_text(json.dumps({"nome": nome, "partes": dados}, ensure_ascii=False,
                                      indent=2), encoding="utf-8")
        tem_thumb = _guardar_thumb(slug, thumb)
        return {"ok": True, "nome": nome, "pecas": len(dados), "thumb": tem_thumb}

    def carregar(self, nome: str) -> dict:
        caminho = _DIR / f"{_slug(nome)}.json"
        if not caminho.is_file():
            return {"erro": f"projeto '{nome}' não encontrado."}
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        partes = plan_scene(dados.get("partes", [])).get("partes", [])
        self.atual = partes
        return {"ok": True, "nome": dados.get("nome", nome), "partes": partes}

    def listar(self) -> list[str]:
        return sorted(p.stem for p in _DIR.glob("*.json"))

    def listar_detalhado(self) -> list[dict]:
        return [{"nome": p.stem, "thumb": (_DIR / f"{p.stem}.png").is_file()}
                for p in sorted(_DIR.glob("*.json"))]

    def caminho_thumb(self, nome: str) -> Path | None:
        p = _DIR / f"{_slug(nome)}.png"
        return p if p.is_file() else None


_store: SceneStore | None = None


def get_store() -> SceneStore:
    global _store
    if _store is None:
        _store = SceneStore()
    return _store
