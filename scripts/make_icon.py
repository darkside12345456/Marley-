"""Gera o ícone do Jarvis (um reator arc) sem dependências externas.

Produz:
  - jarvis/web/static/icon.png  (favicon do HUD)
  - assets/icon.ico             (ícone da app de ambiente de trabalho)

Correr:  python scripts/make_icon.py
"""
from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CYAN = (53, 230, 255)
BG = (7, 20, 38)


def _pixels(size: int) -> bytes:
    cx = cy = size / 2
    maxr = size * 0.47
    aneis = [(0.30, 0.05), (0.42, 0.04), (0.50, 0.03)]  # (raio rel, espessura rel)
    linhas = bytearray()
    for y in range(size):
        linhas.append(0)  # filtro PNG
        for x in range(size):
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            dr = d / size
            # brilho dos anéis
            glow = 0.0
            for rr, t in aneis:
                glow += math.exp(-((dr - rr) / t) ** 2)
            # raios radiais
            ang = math.atan2(dy, dx)
            if 0.30 < dr < 0.42 and (int((ang + math.pi) / (math.pi / 6)) % 1 == 0):
                pass
            # núcleo
            core = math.exp(-((dr / 0.16) ** 2))
            r = BG[0] + (CYAN[0] - BG[0]) * min(1, glow) + core * (255 - BG[0])
            g = BG[1] + (CYAN[1] - BG[1]) * min(1, glow) + core * (255 - BG[1])
            b = BG[2] + (CYAN[2] - BG[2]) * min(1, glow) + core * (255 - BG[2])
            # alfa: círculo com borda suave
            if d > maxr:
                a = 0
            elif d > maxr - 2:
                a = int(255 * (maxr - d) / 2)
            else:
                a = 255
            linhas += bytes((int(max(0, min(255, r))),
                             int(max(0, min(255, g))),
                             int(max(0, min(255, b))), max(0, a)))
    return bytes(linhas)


def _chunk(tipo: bytes, dados: bytes) -> bytes:
    return (struct.pack(">I", len(dados)) + tipo + dados
            + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF))


def _png_bytes(size: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(_pixels(size), 9)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))


def _ico_bytes(png: bytes, size: int) -> bytes:
    # ICO que embute um PNG (suportado pelo Windows Vista+).
    w = h = 0 if size >= 256 else size
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), 22)
    return header + entry + png


def main() -> None:
    png_static = RAIZ / "jarvis" / "web" / "static" / "icon.png"
    png_static.parent.mkdir(parents=True, exist_ok=True)
    png_static.write_bytes(_png_bytes(128))

    assets = RAIZ / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "icon.png").write_bytes(_png_bytes(256))
    (assets / "icon.ico").write_bytes(_ico_bytes(_png_bytes(256), 256))
    print("Ícones gerados: jarvis/web/static/icon.png, assets/icon.png, assets/icon.ico")


if __name__ == "__main__":
    main()
