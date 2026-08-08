"""Ações de interface: como o Jarvis comanda o HUD (abrir páginas, projetar
modelos 3D no Holo-Lab, etc.).

As ferramentas de UI acrescentam ações a um `ActionSink`. Depois de cada
pergunta, o servidor web envia estas ações ao browser, que as executa.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ActionSink:
    items: list[dict] = field(default_factory=list)

    def add(self, tipo: str, **dados) -> None:
        self.items.append({"tipo": tipo, **dados})

    def clear(self) -> None:
        self.items.clear()

    def drain(self) -> list[dict]:
        out = list(self.items)
        self.items.clear()
        return out
