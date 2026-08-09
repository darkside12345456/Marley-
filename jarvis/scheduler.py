"""Agendador de verificações de segurança automáticas.

Corre `verificar_ameacas` em segundo plano de X em X horas, guarda um registo
em data/security_log.jsonl e mantém o último resultado disponível para o HUD.

É um singleton de módulo para que as ferramentas, o servidor web e a CLI
partilhem o mesmo agendador.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime

from . import security
from .config import DATA_DIR

_LOG = DATA_DIR / "security_log.jsonl"


class SecurityScheduler:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.intervalo_horas: float = 0.0
        self.ultima: dict | None = None

    # ------------------------------------------------------------ execução
    def registar(self, rel: dict) -> dict:
        """Guarda um resultado de verificação no histórico (data/security_log.jsonl)."""
        registo = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "nivel": rel.get("nivel"),
            "processos_suspeitos": len(rel.get("processos", {}).get("suspeitos", [])),
            "alertas_rede": len(rel.get("rede", {}).get("alertas", [])),
        }
        self.ultima = {**registo, "relatorio": rel.get("relatorio")}
        try:
            with _LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(registo, ensure_ascii=False) + "\n")
        except Exception:
            pass
        return self.ultima

    def executar_agora(self) -> dict:
        return self.registar(security.verificar_ameacas())

    def historico(self, limite: int = 50) -> list[dict]:
        if not _LOG.exists():
            return []
        linhas = _LOG.read_text(encoding="utf-8").splitlines()
        out = []
        for linha in linhas[-limite:]:
            linha = linha.strip()
            if not linha:
                continue
            try:
                out.append(json.loads(linha))
            except Exception:
                continue
        return out

    # ------------------------------------------------------------ controlo
    def _loop(self) -> None:
        # primeira verificação pouco depois de arrancar
        if self._stop.wait(5):
            return
        self.executar_agora()
        while not self._stop.wait(self.intervalo_horas * 3600):
            self.executar_agora()

    def iniciar(self, intervalo_horas: float) -> dict:
        self.parar()
        if intervalo_horas <= 0:
            self.intervalo_horas = 0.0
            return self.estado()
        self.intervalo_horas = float(intervalo_horas)
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self.estado()

    def parar(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self._thread = None

    @property
    def ativo(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def estado(self) -> dict:
        return {
            "ativo": self.ativo,
            "intervalo_horas": self.intervalo_horas,
            "ultima": self.ultima,
        }


_scheduler: SecurityScheduler | None = None


def get_scheduler() -> SecurityScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = SecurityScheduler()
    return _scheduler
