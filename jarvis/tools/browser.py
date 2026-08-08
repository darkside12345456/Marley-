"""Abertura de páginas web."""
from __future__ import annotations

import re
import urllib.parse

_URL_RE = re.compile(r"^[\w.-]+\.[a-z]{2,}(/|$)", re.IGNORECASE)


def normalizar_url(texto: str) -> dict:
    """Transforma texto em {url, titulo, pesquisa}.

    - URL completo -> abre esse URL
    - domínio simples (ex: 'youtube.com') -> https://…
    - qualquer outra coisa -> pesquisa no Google
    """
    t = (texto or "").strip()
    if not t:
        return {"url": "https://www.google.com", "titulo": "Google", "pesquisa": False}

    if t.startswith(("http://", "https://")):
        return {"url": t, "titulo": t, "pesquisa": False}
    if _URL_RE.match(t):
        return {"url": "https://" + t, "titulo": t, "pesquisa": False}

    q = urllib.parse.quote_plus(t)
    return {
        "url": f"https://www.google.com/search?q={q}",
        "titulo": f"Pesquisa: {t}",
        "pesquisa": True,
    }
