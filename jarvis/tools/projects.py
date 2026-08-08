"""Criador de aplicações — gera projetos-modelo dentro da sandbox 'workspace/'.

Por segurança, tudo é escrito apenas dentro de WORKSPACE_DIR (não toca no resto
do computador).
"""
from __future__ import annotations

import re
from pathlib import Path

from ..config import WORKSPACE_DIR

TIPOS = {"web", "python", "flask", "node", "react", "api"}


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
    if tipo == "react":
        return {
            "index.html": f"""<!DOCTYPE html>
<html lang="pt"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<link rel="stylesheet" href="style.css"></head>
<body><div id="root"></div>
<script type="text/babel" src="app.jsx"></script></body></html>
""",
            "app.jsx": f"""const {{ useState }} = React;
function App() {{
  const [n, setN] = useState(0);
  return (
    <main>
      <h1>{titulo}</h1>
      <p>{desc}</p>
      <button onClick={{() => setN(n + 1)}}>Cliques: {{n}}</button>
    </main>
  );
}}
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
""",
            "style.css": """*{box-sizing:border-box;margin:0}body{font-family:system-ui;
background:#0b1220;color:#eaf6ff;min-height:100vh;display:grid;place-items:center}
main{text-align:center;padding:2rem}h1{color:#35e6ff}button{margin-top:1rem;
padding:.7rem 1.4rem;border:1px solid #35e6ff;background:transparent;color:#35e6ff;
border-radius:8px;cursor:pointer}
""",
            "README.md": f"# {titulo}\n\n{desc}\n\nApp React (via CDN). Abre o `index.html` no browser (requer Internet para carregar o React).\n",
        }
    if tipo == "api":
        return {
            "app.py": '"""' + titulo + ' — API REST com Flask + SQLite (CRUD)."""\n'
                      "import sqlite3\nfrom flask import Flask, request, jsonify\n\n"
                      'app = Flask(__name__)\nDB = "dados.db"\n\n\n'
                      "def db():\n    c = sqlite3.connect(DB)\n    c.row_factory = sqlite3.Row\n"
                      "    c.execute('CREATE TABLE IF NOT EXISTS itens ("
                      "id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)')\n    return c\n\n\n"
                      '@app.route("/itens", methods=["GET"])\ndef listar():\n'
                      "    c = db()\n    linhas = c.execute('SELECT * FROM itens').fetchall()\n"
                      "    return jsonify([dict(l) for l in linhas])\n\n\n"
                      '@app.route("/itens", methods=["POST"])\ndef criar():\n'
                      "    nome = (request.json or {}).get('nome', '')\n    c = db()\n"
                      "    cur = c.execute('INSERT INTO itens (nome) VALUES (?)', (nome,))\n"
                      "    c.commit()\n    return jsonify({'id': cur.lastrowid, 'nome': nome}), 201\n\n\n"
                      '@app.route("/itens/<int:item_id>", methods=["DELETE"])\ndef apagar(item_id):\n'
                      "    c = db()\n    c.execute('DELETE FROM itens WHERE id=?', (item_id,))\n"
                      "    c.commit()\n    return '', 204\n\n\n"
                      'if __name__ == "__main__":\n    app.run(debug=True)\n',
            "requirements.txt": "flask>=3.0\n",
            "README.md": f"# {titulo}\n\n{desc}\n\nAPI REST com SQLite. Endpoints: "
                         "`GET/POST /itens`, `DELETE /itens/<id>`.\n\n"
                         "```bash\npip install -r requirements.txt\npython app.py\n```\n",
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
