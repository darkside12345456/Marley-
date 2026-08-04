"""Operações de ficheiros, restritas à pasta 'workspace' por segurança."""
from __future__ import annotations

from pathlib import Path

from ..config import WORKSPACE_DIR


def _safe(caminho: str | None) -> Path:
    base = WORKSPACE_DIR.resolve()
    alvo = (base / (caminho or "")).resolve()
    if not str(alvo).startswith(str(base)):
        raise ValueError("Acesso fora da área de trabalho não é permitido.")
    return alvo


def list_dir(caminho: str | None = None) -> dict:
    alvo = _safe(caminho)
    if not alvo.exists():
        return {"erro": "caminho inexistente", "caminho": caminho}
    itens = []
    for p in sorted(alvo.iterdir()):
        itens.append({"nome": p.name, "tipo": "pasta" if p.is_dir() else "ficheiro"})
    return {"caminho": str(alvo.relative_to(WORKSPACE_DIR.resolve())) or ".", "itens": itens}


def read_file(caminho: str) -> dict:
    alvo = _safe(caminho)
    if not alvo.is_file():
        return {"erro": "ficheiro inexistente", "caminho": caminho}
    texto = alvo.read_text(encoding="utf-8", errors="replace")
    if len(texto) > 8000:
        texto = texto[:8000] + "\n… (truncado)"
    return {"caminho": caminho, "conteudo": texto}


def write_file(caminho: str, conteudo: str) -> dict:
    alvo = _safe(caminho)
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(conteudo, encoding="utf-8")
    return {"ok": True, "caminho": caminho, "bytes": len(conteudo.encode("utf-8"))}
