"""Objetivo/meta com progresso (ex: chegar a 100 000). Guardado em data/meta.json."""
from __future__ import annotations

import json

from .config import DATA_DIR, config

_FILE = DATA_DIR / "meta.json"


def get_meta() -> dict:
    dados = {}
    if _FILE.exists():
        try:
            dados = json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            dados = {}
    alvo = float(dados.get("alvo", config.meta_target)) or 1.0
    atual = float(dados.get("atual", 0))
    label = dados.get("label", config.meta_label)
    return {"alvo": alvo, "atual": atual, "label": label,
            "percent": round(min(100.0, atual / alvo * 100), 1)}


def set_meta(atual=None, alvo=None, label=None) -> dict:
    m = get_meta()
    if atual is not None:
        try:
            m["atual"] = max(0.0, float(atual))
        except (TypeError, ValueError):
            pass
    if alvo is not None:
        try:
            m["alvo"] = max(1.0, float(alvo))
        except (TypeError, ValueError):
            pass
    if label is not None:
        m["label"] = str(label)[:40]
    _FILE.write_text(json.dumps({"alvo": m["alvo"], "atual": m["atual"], "label": m["label"]},
                                ensure_ascii=False), encoding="utf-8")
    return get_meta()
