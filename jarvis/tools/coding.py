"""Escrita de código em qualquer linguagem, guardado na sandbox 'workspace/'."""
from __future__ import annotations

import re
from pathlib import Path

from ..config import WORKSPACE_DIR

# Linguagem -> extensão de ficheiro (lista abrangente).
LINGUAGENS = {
    "python": "py", "javascript": "js", "js": "js", "typescript": "ts", "ts": "ts",
    "java": "java", "c": "c", "c++": "cpp", "cpp": "cpp", "c#": "cs", "csharp": "cs",
    "go": "go", "golang": "go", "rust": "rs", "ruby": "rb", "php": "php", "swift": "swift",
    "kotlin": "kt", "html": "html", "css": "css", "sql": "sql", "bash": "sh", "shell": "sh",
    "powershell": "ps1", "r": "r", "lua": "lua", "perl": "pl", "scala": "scala", "dart": "dart",
    "haskell": "hs", "julia": "jl", "matlab": "m", "objective-c": "m", "assembly": "asm",
    "fortran": "f90", "cobol": "cob", "elixir": "ex", "erlang": "erl", "clojure": "clj",
    "fsharp": "fs", "f#": "fs", "groovy": "groovy", "vb": "vb", "visualbasic": "vb",
    "json": "json", "yaml": "yaml", "xml": "xml", "markdown": "md", "solidity": "sol",
    "zig": "zig", "nim": "nim", "ocaml": "ml", "crystal": "cr", "vhdl": "vhd", "verilog": "v",
    "graphql": "graphql", "dockerfile": "dockerfile", "makefile": "mk", "toml": "toml",
}


def extensao(linguagem: str) -> str:
    return LINGUAGENS.get((linguagem or "").lower().strip(), "txt")


def _slug(nome: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_.\-/]+", "-", (nome or "codigo").strip()).strip("-/")
    return s or "codigo"


def guardar_codigo(nome: str, linguagem: str, codigo: str) -> dict:
    base = WORKSPACE_DIR.resolve()
    ext = extensao(linguagem)
    nome = _slug(nome)
    if "." not in Path(nome).name:
        nome = f"{nome}.{ext}"
    alvo = (base / nome).resolve()
    if not str(alvo).startswith(str(base)):
        return {"erro": "Caminho fora da área de trabalho."}
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(codigo or "", encoding="utf-8")
    rel = alvo.relative_to(base)
    return {"ok": True, "ficheiro": f"workspace/{rel}", "linguagem": linguagem,
            "linhas": (codigo or "").count("\n") + 1}
