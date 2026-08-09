"""Notícias e novidades em tempo real (via Google News RSS, gratuito, sem chave).

O modelo local tem conhecimento "congelado" na data de treino; esta ferramenta
traz informação atual de QUALQUER campo — basta usar o tema como pesquisa.
"""
from __future__ import annotations

import urllib.parse
import urllib.request
from xml.etree import ElementTree as ET

_BASE = "https://news.google.com/rss"
_LOCALE = "hl=pt-PT&gl=PT&ceid=PT:pt"

# Atalhos de categoria -> pesquisa.
CATEGORIAS = {
    "mundo": "mundo", "portugal": "Portugal", "tecnologia": "tecnologia",
    "ciência": "ciência", "ciencia": "ciência", "economia": "economia",
    "desporto": "desporto", "saúde": "saúde", "saude": "saúde",
    "cultura": "cultura", "política": "política", "politica": "política",
    "ia": "inteligência artificial", "clima": "clima ambiente",
}


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Sonny/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def obter_noticias(tema: str = "", limite: int = 8) -> dict:
    limite = max(1, min(15, int(limite or 8)))
    tema = (tema or "").strip()
    consulta = CATEGORIAS.get(tema.lower(), tema)

    if consulta:
        url = f"{_BASE}/search?q={urllib.parse.quote(consulta)}&{_LOCALE}"
    else:
        url = f"{_BASE}?{_LOCALE}"  # principais manchetes

    try:
        root = ET.fromstring(_fetch(url))
    except Exception as exc:  # noqa: BLE001
        return {"erro": f"não consegui obter notícias: {exc}",
                "nota": "É preciso ligação à Internet."}

    noticias = []
    for item in root.findall(".//item")[:limite]:
        titulo = (item.findtext("title") or "").strip()
        fonte_el = item.find("source")
        fonte = ((fonte_el.text if fonte_el is not None else "") or "").strip()
        # o título do Google News costuma terminar em " - Fonte"; separa-o
        if fonte and titulo.endswith(f" - {fonte}"):
            titulo = titulo[: -len(f" - {fonte}")].rstrip()
        elif not fonte and " - " in titulo:
            titulo, _, fonte = titulo.rpartition(" - ")
        noticias.append({
            "titulo": titulo,
            "fonte": fonte,
            "data": (item.findtext("pubDate") or "").strip(),
            "link": (item.findtext("link") or "").strip(),
        })

    return {"tema": consulta or "principais manchetes", "noticias": noticias}
