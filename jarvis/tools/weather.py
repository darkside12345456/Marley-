"""Meteorologia via Open-Meteo (gratuito, sem chave de API)."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

_CODES = {
    0: "céu limpo", 1: "maioritariamente limpo", 2: "parcialmente nublado",
    3: "nublado", 45: "nevoeiro", 48: "nevoeiro gelado", 51: "chuvisco fraco",
    53: "chuvisco", 55: "chuvisco forte", 61: "chuva fraca", 63: "chuva",
    65: "chuva forte", 71: "neve fraca", 73: "neve", 75: "neve forte",
    80: "aguaceiros", 81: "aguaceiros fortes", 82: "aguaceiros violentos",
    95: "trovoada", 96: "trovoada com granizo", 99: "trovoada com granizo forte",
}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Jarvis/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_weather(local: str) -> dict:
    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urllib.parse.urlencode({"name": local, "count": 1, "language": "pt"})
    )
    geo = _get(geo_url)
    if not geo.get("results"):
        return {"erro": f"Não encontrei a localidade '{local}'."}
    place = geo["results"][0]
    lat, lon = place["latitude"], place["longitude"]

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "timezone": "auto",
                "forecast_days": 1,
            }
        )
    )
    data = _get(url)
    cur = data.get("current", {})
    daily = data.get("daily", {})
    code = cur.get("weather_code")
    return {
        "local": f"{place['name']}, {place.get('country', '')}".strip(", "),
        "condicao": _CODES.get(code, "desconhecida"),
        "temperatura_c": cur.get("temperature_2m"),
        "sensacao_c": cur.get("apparent_temperature"),
        "humidade_pct": cur.get("relative_humidity_2m"),
        "vento_kmh": cur.get("wind_speed_10m"),
        "max_c": (daily.get("temperature_2m_max") or [None])[0],
        "min_c": (daily.get("temperature_2m_min") or [None])[0],
    }
