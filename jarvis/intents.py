"""Respostas diretas e rápidas para pedidos comuns.

Isto responde a horas, tempo, data e notícias **sem passar pelo modelo** — vai
direto às ferramentas (APIs gratuitas). Assim funciona de forma fiável e
instantânea, mesmo que o modelo local seja lento ou esteja indisponível.

Se o pedido não encaixar em nenhum destes padrões, devolve None e o pedido
segue para o modelo (LLM) como habitualmente.
"""
from __future__ import annotations

import re

from .tools import basics, weather, news, web

# palavra(s) de ligação antes do local: "em Lisboa", "no Porto", "de Tóquio"…
_LOC_RE = re.compile(r"\b(?:em|no|na|nos|nas|de|do|da|para|in)\s+(.+)$", re.IGNORECASE)
_LIMPAR = re.compile(r"\b(agora|hoje|neste momento|por favor|sff|pf)\b", re.IGNORECASE)


def _local(t: str) -> str:
    m = _LOC_RE.search(t)
    if not m:
        return ""
    loc = _LIMPAR.sub("", m.group(1)).strip(" ?.!¿¡\"'")
    return loc


def responder(texto: str) -> str | None:
    t = (texto or "").lower().strip()
    if not t:
        return None
    loc = _local(t)

    # --- METEOROLOGIA ---
    if re.search(r"\b(tempo|meteorolog|temperatura|clima|chuv|graus|est[aá]\s+(calor|frio))\b", t):
        if not loc:
            return "De que cidade queres saber o tempo? (por exemplo: “tempo em Lisboa”)"
        w = weather.get_weather(loc)
        if "erro" in w:
            return f"Não consegui a meteorologia de {loc}: {w['erro']}"
        return (f"Em {w['local']} está {w['condicao']}, {w['temperatura_c']}°C "
                f"(sensação de {w['sensacao_c']}°C). Máxima {w['max_c']}°C e mínima "
                f"{w['min_c']}°C, vento {w['vento_kmh']} km/h e humidade {w['humidade_pct']}%.")

    # --- HORAS ---
    if re.search(r"\b(que horas|horas s[aã]o|s[aã]o horas|que hora|hora certa|horas)\b", t):
        h = basics.current_time(loc)
        if "erro" in h:
            return f"Não consegui saber as horas: {h['erro']}"
        if h.get("local", "aqui") == "aqui":
            return f"São {h['hora']} ({h['data']}, {h['dia_semana']})."
        return f"Em {h['local']} são {h['hora']} ({h['dia_semana']})."

    # --- DATA ---
    if re.search(r"\b(que dia (é|e)|dia de hoje|data de hoje|em que dia|hoje (é|e))\b", t):
        h = basics.current_time("")
        return f"Hoje é {h['dia_semana']}, {h['data']}."

    # --- PESQUISA NA WEB (informação real) ---
    m = re.match(r"^(?:pesquisa|pesquisar|procura|procurar|busca|buscar|"
                 r"o que (?:é|e|s[ãa]o)|quem (?:é|e|foi|s[ãa]o))\s+(?:por\s+|sobre\s+)?(.+)$", t)
    if m:
        consulta = m.group(1).strip(" ?.!\"'")
        r = web.web_search(consulta)
        if "erro" in r:
            return f"Não consegui pesquisar (precisa de Internet): {r['erro']}"
        res = r.get("resultados") or []
        if not res:
            return r.get("nota") or f"Não encontrei resultados para “{consulta}”."
        linhas = []
        for it in res[:3]:
            resumo = (it.get("resumo") or "").strip()
            fonte = it.get("fonte") or ""
            if resumo:
                linhas.append("• " + resumo + (f"  ({fonte})" if fonte else ""))
        return f"Sobre “{consulta}”:\n" + "\n".join(linhas)

    # --- NOTÍCIAS ---
    if re.search(r"\b(not[ií]cias|novidades|[uú]ltimas)\b", t):
        r = news.obter_noticias(loc or "", 6)
        if "erro" in r:
            return f"Não consegui as notícias: {r['erro']}"
        if not r.get("noticias"):
            return "Não encontrei notícias para esse tema agora."
        linhas = [f"• {n['titulo']}" + (f" — {n['fonte']}" if n.get("fonte") else "")
                  for n in r["noticias"]]
        return f"Últimas notícias de {r['tema']}:\n" + "\n".join(linhas)

    return None
