"""Ferramentas básicas."""
from __future__ import annotations

from datetime import datetime


def current_time() -> str:
    agora = datetime.now()
    dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    dia = dias[agora.weekday()]
    return agora.strftime(f"%d/%m/%Y %H:%M ({dia}-feira)")
