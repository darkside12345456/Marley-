"""Geração de malhas 3D e exportação para .obj.

Gera geometria (vértices + faces) para as peças do Holo-Lab e serializa em
formato Wavefront .obj — o formato aberto que qualquer software 3D e a maioria
dos fatiadores de impressão 3D conseguem abrir.

Nota: as peças "sólidas" (esfera, toroide, cilindro, estrutura) exportam faces
prontas a visualizar/imprimir; o reator é um design plano em linhas (wireframe).
"""
from __future__ import annotations

import math
from pathlib import Path

Vec = tuple[float, float, float]


def _uv_sphere(seg: int = 24, rings: int = 16, R: float = 1.0):
    verts: list[Vec] = []
    for i in range(rings + 1):
        lat = -math.pi / 2 + math.pi * i / rings
        for j in range(seg):
            lon = 2 * math.pi * j / seg
            verts.append((R * math.cos(lat) * math.cos(lon),
                          R * math.sin(lat),
                          R * math.cos(lat) * math.sin(lon)))
    faces = []
    idx = lambda i, j: i * seg + (j % seg) + 1  # noqa: E731  (1-based p/ OBJ)
    for i in range(rings):
        for j in range(seg):
            faces.append((idx(i, j), idx(i, j + 1), idx(i + 1, j + 1), idx(i + 1, j)))
    return verts, faces, []


def _torus(R: float = 0.85, r: float = 0.35, seg: int = 32, side: int = 16):
    verts: list[Vec] = []
    for i in range(seg):
        u = 2 * math.pi * i / seg
        for j in range(side):
            w = 2 * math.pi * j / side
            verts.append(((R + r * math.cos(w)) * math.cos(u),
                          r * math.sin(w),
                          (R + r * math.cos(w)) * math.sin(u)))
    faces = []
    idx = lambda i, j: (i % seg) * side + (j % side) + 1  # noqa: E731
    for i in range(seg):
        for j in range(side):
            faces.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
    return verts, faces, []


def _cylinder(R: float = 0.7, h: float = 1.6, seg: int = 24):
    verts: list[Vec] = []
    for k in (0, 1):
        y = -h / 2 + k * h
        for j in range(seg):
            a = 2 * math.pi * j / seg
            verts.append((R * math.cos(a), y, R * math.sin(a)))
    faces = []
    idx = lambda k, j: k * seg + (j % seg) + 1  # noqa: E731
    for j in range(seg):
        faces.append((idx(0, j), idx(0, j + 1), idx(1, j + 1), idx(1, j)))
    # tampas (leque a partir do centro)
    cb = len(verts) + 1
    verts.append((0, -h / 2, 0))
    ct = len(verts) + 1
    verts.append((0, h / 2, 0))
    for j in range(seg):
        faces.append((cb, idx(0, j + 1), idx(0, j)))
        faces.append((ct, idx(1, j), idx(1, j + 1)))
    return verts, faces, []


def _box(s: float = 1.0):
    verts = [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
             (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]
    faces = [(1, 2, 3, 4), (5, 8, 7, 6), (1, 5, 6, 2),
             (2, 6, 7, 3), (3, 7, 8, 4), (4, 8, 5, 1)]
    return verts, faces, []


def _reactor(seg: int = 36):
    verts: list[Vec] = []
    edges: list[tuple[int, int]] = []
    for R in (0.35, 0.6, 0.9, 1.05):
        base = len(verts)
        for j in range(seg):
            a = 2 * math.pi * j / seg
            verts.append((R * math.cos(a), 0.0, R * math.sin(a)))
        for j in range(seg):
            edges.append((base + j + 1, base + (j + 1) % seg + 1))
    return verts, [], edges


_BUILDERS = {
    "esfera": lambda seg: _uv_sphere(seg or 24, 16),
    "capacete": lambda seg: _uv_sphere(seg or 24, 16),
    "toroide": lambda seg: _torus(seg=seg or 32),
    "cilindro": lambda seg: _cylinder(seg=seg or 24),
    "manopla": lambda seg: _cylinder(R=0.55, h=1.5, seg=seg or 20),
    "estrutura": lambda seg: _box(1.0),
    "reator": lambda seg: _reactor(seg or 36),
}


def gerar_obj(forma: str, escala: float = 1.0, segmentos: int = 0) -> str:
    """Devolve o texto .obj de uma peça."""
    build = _BUILDERS.get(forma, _BUILDERS["reator"])
    verts, faces, edges = build(int(segmentos) if segmentos else 0)
    linhas = ["# Exportado pelo Jarvis Holo-Lab", f"o {forma}"]
    for v in verts:
        linhas.append(f"v {v[0] * escala:.5f} {v[1] * escala:.5f} {v[2] * escala:.5f}")
    for f in faces:
        linhas.append("f " + " ".join(str(i) for i in f))
    for e in edges:
        linhas.append(f"l {e[0]} {e[1]}")
    return "\n".join(linhas) + "\n"


def exportar_obj(forma: str, destino: Path, escala: float = 1.0, segmentos: int = 0) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_obj(forma, escala, segmentos), encoding="utf-8")
    return destino
