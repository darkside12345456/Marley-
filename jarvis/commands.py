"""Comandos de sistema à espera de confirmação do utilizador.

Quando a Sonny quer correr um comando, ele fica AQUI (pendente) e só é
executado quando o utilizador confirma explicitamente. Isto garante que nenhum
comando corre sem aprovação, mesmo com o modo de shell ligado.

Segurança: a execução é feita por id (o servidor só corre comandos que foram
propostos pela Sonny e ainda estão pendentes) — nunca comandos arbitrários
vindos do pedido HTTP.
"""
from __future__ import annotations

import time
import uuid

_TTL = 600  # segundos até um comando pendente expirar


class PendingCommands:
    def __init__(self) -> None:
        self._d: dict[str, dict] = {}

    def add(self, comando: str) -> str:
        self._limpar()
        cid = uuid.uuid4().hex[:12]
        self._d[cid] = {"comando": comando, "ts": time.time()}
        return cid

    def pop(self, cid: str) -> str | None:
        self._limpar()
        item = self._d.pop(cid or "", None)
        return item["comando"] if item else None

    def _limpar(self) -> None:
        agora = time.time()
        for k in list(self._d):
            if agora - self._d[k]["ts"] > _TTL:
                self._d.pop(k, None)


_pending: PendingCommands | None = None


def get_pending() -> PendingCommands:
    global _pending
    if _pending is None:
        _pending = PendingCommands()
    return _pending
