"""Geração de malhas 3D sólidas e exportação para .obj.

Todas as peças são geradas como **sólidos fechados (watertight)** — malhas
manifold em que cada aresta é partilhada por exatamente duas faces. Isto garante
que o ficheiro .obj é adequado para impressão 3D (um fatiador consegue fatiá-lo).

A função `is_watertight` valida essa propriedade e é usada nos testes.
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

Vec = tuple[float, float, float]


# ------------------------------------------------------------- construtores
def _sphere(seg: int = 24, rings: int = 16, R: float = 1.0):
    seg = max(6, seg)
    rings = max(3, rings)
    verts: list[Vec] = []
    faces: list[tuple] = []
    aneis: list[list[int]] = []
    for i in range(1, rings):
        lat = -math.pi / 2 + math.pi * i / rings
        y, rr = R * math.sin(lat), R * math.cos(lat)
        linha = []
        for k in range(seg):
            lon = 2 * math.pi * k / seg
            linha.append(len(verts))
            verts.append((rr * math.cos(lon), y, rr * math.sin(lon)))
        aneis.append(linha)
    sul = len(verts); verts.append((0, -R, 0))
    norte = len(verts); verts.append((0, R, 0))
    primeiro = aneis[0]
    for k in range(seg):
        faces.append((sul, primeiro[k], primeiro[(k + 1) % seg]))
    for i in range(len(aneis) - 1):
        a, b = aneis[i], aneis[i + 1]
        for k in range(seg):
            faces.append((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    ultimo = aneis[-1]
    for k in range(seg):
        faces.append((norte, ultimo[(k + 1) % seg], ultimo[k]))
    return verts, faces


def _torus(R: float = 0.85, r: float = 0.35, seg: int = 32, side: int = 16):
    seg, side = max(6, seg), max(6, side)
    verts: list[Vec] = []
    for i in range(seg):
        u = 2 * math.pi * i / seg
        for j in range(side):
            w = 2 * math.pi * j / side
            verts.append(((R + r * math.cos(w)) * math.cos(u),
                          r * math.sin(w),
                          (R + r * math.cos(w)) * math.sin(u)))
    idx = lambda i, j: (i % seg) * side + (j % side)  # noqa: E731
    faces = []
    for i in range(seg):
        for j in range(side):
            faces.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
    return verts, faces


def _cylinder(R: float = 0.7, h: float = 1.6, seg: int = 24):
    seg = max(6, seg)
    verts: list[Vec] = []
    baixo, cima = [], []
    for j in range(seg):
        a = 2 * math.pi * j / seg
        baixo.append(len(verts)); verts.append((R * math.cos(a), -h / 2, R * math.sin(a)))
    for j in range(seg):
        a = 2 * math.pi * j / seg
        cima.append(len(verts)); verts.append((R * math.cos(a), h / 2, R * math.sin(a)))
    cb = len(verts); verts.append((0, -h / 2, 0))
    ct = len(verts); verts.append((0, h / 2, 0))
    faces = []
    for j in range(seg):
        n = (j + 1) % seg
        faces.append((baixo[j], baixo[n], cima[n], cima[j]))
        faces.append((cb, baixo[n], baixo[j]))
        faces.append((ct, cima[j], cima[n]))
    return verts, faces


def _box(s: float = 1.0):
    verts = [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
             (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return verts, faces


def _reactor(seg: int = 36, Ro: float = 1.05, Ri: float = 0.5, h: float = 0.24):
    """Reator como anel sólido (prisma anular) — fechado e imprimível."""
    seg = max(8, seg)
    verts: list[Vec] = []

    def anel(R, y):
        r = []
        for j in range(seg):
            a = 2 * math.pi * j / seg
            r.append(len(verts)); verts.append((R * math.cos(a), y, R * math.sin(a)))
        return r

    to, ti = anel(Ro, h / 2), anel(Ri, h / 2)
    bo, bi = anel(Ro, -h / 2), anel(Ri, -h / 2)
    faces = []
    for j in range(seg):
        n = (j + 1) % seg
        faces.append((to[j], to[n], ti[n], ti[j]))   # topo
        faces.append((bi[j], bi[n], bo[n], bo[j]))    # base
        faces.append((bo[j], bo[n], to[n], to[j]))    # parede exterior
        faces.append((ti[j], ti[n], bi[n], bi[j]))    # parede interior
    return verts, faces


def _dome(seg: int = 24, rings: int = 8, R: float = 1.0):
    """Cúpula (capacete) com base fechada."""
    seg, rings = max(8, seg), max(3, rings)
    verts: list[Vec] = []
    faces = []
    aneis = []
    for i in range(1, rings):
        lat = (math.pi / 2) * (i / rings)
        y, rr = R * math.sin(lat), R * math.cos(lat)
        linha = []
        for k in range(seg):
            lon = 2 * math.pi * k / seg
            linha.append(len(verts)); verts.append((rr * math.cos(lon), y, rr * math.sin(lon)))
        aneis.append(linha)
    eq = []
    for k in range(seg):
        lon = 2 * math.pi * k / seg
        eq.append(len(verts)); verts.append((R * math.cos(lon), 0, R * math.sin(lon)))
    norte = len(verts); verts.append((0, R, 0))
    centro = len(verts); verts.append((0, 0, 0))
    for k in range(seg):
        faces.append((centro, eq[(k + 1) % seg], eq[k]))          # base
    primeiro = aneis[0]
    for k in range(seg):
        faces.append((eq[k], eq[(k + 1) % seg], primeiro[(k + 1) % seg], primeiro[k]))
    for i in range(len(aneis) - 1):
        a, b = aneis[i], aneis[i + 1]
        for k in range(seg):
            faces.append((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    ultimo = aneis[-1]
    for k in range(seg):
        faces.append((norte, ultimo[(k + 1) % seg], ultimo[k]))
    return verts, faces


_BUILDERS = {
    "esfera": lambda seg: _sphere(seg or 24, 16),
    "capacete": lambda seg: _dome(seg or 24, 8),
    "toroide": lambda seg: _torus(seg=seg or 32),
    "cilindro": lambda seg: _cylinder(seg=seg or 24),
    "manopla": lambda seg: _cylinder(R=0.55, h=1.5, seg=seg or 20),
    "estrutura": lambda seg: _box(1.0),
    "reator": lambda seg: _reactor(seg or 36),
}


# --------------------------------------------------------------- utilitários
def is_watertight(verts, faces) -> bool:
    """Verdadeiro se a malha for fechada (cada aresta em exatamente 2 faces)."""
    arestas: Counter = Counter()
    for f in faces:
        n = len(f)
        for i in range(n):
            a, b = f[i], f[(i + 1) % n]
            if a == b:
                return False
            arestas[frozenset((a, b))] += 1
    return len(arestas) > 0 and all(c == 2 for c in arestas.values())


def construir(forma: str, segmentos: int = 0):
    build = _BUILDERS.get(forma, _BUILDERS["reator"])
    return build(int(segmentos) if segmentos else 0)


def gerar_obj(forma: str, escala: float = 1.0, segmentos: int = 0) -> str:
    verts, faces = construir(forma, segmentos)
    linhas = ["# Exportado pelo Jarvis Holo-Lab (solido fechado)", f"o {forma}"]
    for v in verts:
        linhas.append(f"v {v[0] * escala:.5f} {v[1] * escala:.5f} {v[2] * escala:.5f}")
    for f in faces:
        linhas.append("f " + " ".join(str(i + 1) for i in f))  # OBJ é 1-based
    return "\n".join(linhas) + "\n"


def exportar_obj(forma: str, destino: Path, escala: float = 1.0, segmentos: int = 0) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_obj(forma, escala, segmentos), encoding="utf-8")
    return destino


def _rot(p, rot):
    """Aplica rotação (rx, ry, rz) — mesma ordem do editor 3D."""
    x, y, z = p
    rx, ry, rz = rot
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return x, y, z


def gerar_obj_cena(partes) -> str:
    """Exporta uma cena inteira (várias peças) como um único sólido .obj.

    Cada peça é transformada (rotação, escala, posição) e as faces são
    reindexadas, produzindo uma malha combinada pronta a fatiar.
    """
    linhas = ["# Cena exportada pelo Jarvis Holo-Lab (solido combinado)"]
    offset = 0
    for idx, parte in enumerate(partes or []):
        if not isinstance(parte, dict):
            continue
        forma = parte.get("forma", "reator")
        escala = float(parte.get("escala", 1) or 1)
        seg = int(parte.get("segmentos", 0) or 0)
        rot = parte.get("rot") or [0, 0, 0]
        pos = parte.get("pos") or [0, 0, 0]
        verts, faces = construir(forma, seg)
        linhas.append(f"o peca{idx + 1}_{forma}")
        for v in verts:
            rx, ry, rz = _rot(v, rot)
            linhas.append(f"v {rx * escala + pos[0]:.5f} "
                          f"{ry * escala + pos[1]:.5f} {rz * escala + pos[2]:.5f}")
        for f in faces:
            linhas.append("f " + " ".join(str(i + 1 + offset) for i in f))
        offset += len(verts)
    return "\n".join(linhas) + "\n"
