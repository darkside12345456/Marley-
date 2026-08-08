"""Criador de aplicações — gera projetos-modelo dentro da sandbox 'workspace/'.

Por segurança, tudo é escrito apenas dentro de WORKSPACE_DIR (não toca no resto
do computador).
"""
from __future__ import annotations

import re
from pathlib import Path

from ..config import WORKSPACE_DIR

TIPOS = {"web", "python", "flask", "node"}


def _slug(nome: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", (nome or "app").strip().lower()).strip("-")
    return s or "app"


def _safe_dir(nome: str) -> Path:
    base = WORKSPACE_DIR.resolve()
    alvo = (base / _slug(nome)).resolve()
    if not str(alvo).startswith(str(base)):
        raise ValueError("Caminho fora da área de trabalho.")
    return alvo


def _templates(tipo: str, nome: str, descricao: str) -> dict[str, str]:
    titulo = nome or "Aplicação"
    desc = descricao or "Aplicação gerada pelo Jarvis."
    if tipo == "web":
        return {
            "index.html": f"""<!DOCTYPE html>
<html lang="pt"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title><link rel="stylesheet" href="style.css"></head>
<body><main><h1>{titulo}</h1><p>{desc}</p>
<button id="btn">Clica-me</button><p id="saida"></p></main>
<script src="app.js"></script></body></html>
""",
            "style.css": """*{box-sizing:border-box;margin:0}body{font-family:system-ui;
background:#0b1220;color:#eaf6ff;min-height:100vh;display:grid;place-items:center}
main{text-align:center;padding:2rem}h1{color:#35e6ff}button{margin-top:1rem;
padding:.7rem 1.4rem;border:1px solid #35e6ff;background:transparent;color:#35e6ff;
border-radius:8px;cursor:pointer}button:hover{background:#35e6ff22}
""",
            "app.js": """let n=0;document.getElementById('btn').addEventListener('click',()=>{
n++;document.getElementById('saida').textContent='Cliques: '+n;});
""",
        }
    if tipo == "python":
        return {
            "main.py": f'"""{titulo} — {desc}"""\n\n\n'
                       'def main():\n    print("Olá do ' + titulo + '!")\n\n\n'
                       'if __name__ == "__main__":\n    main()\n',
            "README.md": f"# {titulo}\n\n{desc}\n\n## Correr\n\n```bash\npython main.py\n```\n",
        }
    if tipo == "flask":
        return {
            "app.py": 'from flask import Flask\n\napp = Flask(__name__)\n\n\n'
                      '@app.route("/")\ndef home():\n    return "'
                      + titulo + ' online!"\n\n\n'
                      'if __name__ == "__main__":\n    app.run(debug=True)\n',
            "requirements.txt": "flask>=3.0\n",
            "README.md": f"# {titulo}\n\n{desc}\n\n```bash\npip install -r requirements.txt\npython app.py\n```\n",
        }
    # node
    return {
        "index.js": f'// {titulo} — {desc}\nconsole.log("Olá do {titulo}!");\n',
        "package.json": '{\n  "name": "' + _slug(nome) + '",\n  "version": "1.0.0",\n'
                        '  "main": "index.js",\n  "scripts": {"start": "node index.js"}\n}\n',
    }


def criar_projeto(nome: str, tipo: str = "web", descricao: str = "") -> dict:
    """Cria a estrutura de um projeto e devolve os ficheiros criados."""
    tipo = (tipo or "web").lower().strip()
    if tipo not in TIPOS:
        return {"erro": f"tipo inválido '{tipo}'. Usa: {', '.join(sorted(TIPOS))}."}

    pasta = _safe_dir(nome)
    pasta.mkdir(parents=True, exist_ok=True)
    ficheiros = _templates(tipo, nome, descricao)
    for rel, conteudo in ficheiros.items():
        (pasta / rel).write_text(conteudo, encoding="utf-8")

    rel_pasta = pasta.relative_to(WORKSPACE_DIR.resolve())
    resultado = {
        "ok": True,
        "tipo": tipo,
        "pasta": str(rel_pasta),
        "ficheiros": list(ficheiros),
    }
    if tipo in {"web"}:
        # URL servido pelo HUD para abrir a app no browser.
        resultado["abrir_url"] = f"/workspace/{rel_pasta.as_posix()}/index.html"
    return resultado
