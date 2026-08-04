"""Pesquisa web via DuckDuckGo Instant Answer (gratuito, sem chave)."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Jarvis/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def web_search(consulta: str) -> dict:
    url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode(
        {"q": consulta, "format": "json", "no_html": 1, "skip_disambig": 1}
    )
    data = _get(url)

    resultados = []
    if data.get("AbstractText"):
        resultados.append(
            {"titulo": data.get("Heading", consulta), "resumo": data["AbstractText"],
             "fonte": data.get("AbstractURL", "")}
        )
    for item in data.get("RelatedTopics", []):
        if "Text" in item:
            resultados.append({"resumo": item["Text"], "fonte": item.get("FirstURL", "")})
        if len(resultados) >= 5:
            break

    if not resultados:
        return {"consulta": consulta, "resultados": [],
                "nota": "Sem resposta direta. Tenta reformular a pesquisa."}
    return {"consulta": consulta, "resultados": resultados[:5]}
