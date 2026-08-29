"""Ferramentas básicas: horas (local ou de qualquer cidade) e data."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime

_DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
         "sexta-feira", "sábado", "domingo"]


def _semana(d: datetime) -> str:
    return _DIAS[d.weekday()]


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Sonny/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def _geocode(local: str) -> dict | None:
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
        {"name": local, "count": 1, "language": "pt"})
    g = _get(url)
    res = g.get("results") or []
    return res[0] if res else None


def current_time(local: str = "") -> dict:
    """Horas locais (sem argumento) ou de qualquer cidade do mundo (com fuso)."""
    local = (local or "").strip()
    if not local:
        agora = datetime.now()
        return {"local": "aqui", "hora": agora.strftime("%H:%M"),
                "data": agora.strftime("%d/%m/%Y"), "dia_semana": _semana(agora)}

    try:
        place = _geocode(local)
    except Exception as exc:  # noqa: BLE001
        return {"erro": f"não consegui contactar o serviço de horas ({exc}).",
                "nota": "é preciso ligação à Internet."}
    if not place:
        return {"erro": f"não encontrei a localidade '{local}'."}

    tz = place.get("timezone")
    nome = f"{place.get('name', local)}, {place.get('country', '')}".strip(", ")
    agora = None
    # 1) via fuso horário (preciso)
    try:
        from zoneinfo import ZoneInfo
        agora = datetime.now(ZoneInfo(tz))
    except Exception:
        # 2) alternativa: hora local devolvida pela API de previsão
        try:
            fc = _get("https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(
                {"latitude": place["latitude"], "longitude": place["longitude"],
                 "current": "temperature_2m", "timezone": "auto"}))
            ts = (fc.get("current") or {}).get("time")
            if ts:
                agora = datetime.fromisoformat(ts)
        except Exception:
            agora = None
    if agora is None:
        return {"erro": f"não consegui o fuso horário de '{local}'."}

    return {"local": nome, "fuso": tz, "hora": agora.strftime("%H:%M"),
            "data": agora.strftime("%d/%m/%Y"), "dia_semana": _semana(agora)}
