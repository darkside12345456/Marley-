"""Telemetria do sistema para o HUD (CPU, RAM, disco, IP local, uptime).

Usa psutil se estiver disponível; caso contrário recorre à biblioteca padrão
(/proc no Linux, loadavg, shutil) para dar valores reais na maioria dos casos.
Tudo é leitura local — nada é enviado para fora.
"""
from __future__ import annotations

import os
import shutil
import socket
import time

try:
    import psutil  # type: ignore
    _HAS_PSUTIL = True
except Exception:  # pragma: no cover
    _HAS_PSUTIL = False

_START = time.time()


def _cpu():
    if _HAS_PSUTIL:
        try:
            return round(psutil.cpu_percent(interval=0.0), 1)
        except Exception:
            pass
    if hasattr(os, "getloadavg"):
        try:
            n = os.cpu_count() or 1
            return round(min(100.0, os.getloadavg()[0] / n * 100), 1)
        except Exception:
            pass
    return None


def _ram():
    if _HAS_PSUTIL:
        try:
            return round(psutil.virtual_memory().percent, 1)
        except Exception:
            pass
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                chave, _, resto = line.partition(":")
                info[chave] = int(resto.strip().split()[0])
        total, disp = info.get("MemTotal"), info.get("MemAvailable")
        if total and disp:
            return round((1 - disp / total) * 100, 1)
    except Exception:
        pass
    return None


def _disco():
    try:
        u = shutil.disk_usage(os.path.expanduser("~"))
        return round(u.used / u.total * 100, 1)
    except Exception:
        return None


def _ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("10.255.255.255", 1))  # não envia dados; só escolhe a interface
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def get_telemetry() -> dict:
    return {
        "cpu": _cpu(),
        "ram": _ram(),
        "disco": _disco(),
        "ip": _ip(),
        "uptime": int(time.time() - _START),
        "psutil": _HAS_PSUTIL,
    }
