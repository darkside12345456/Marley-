"""Planeamento de modelos 3D para o Holo-Lab.

Traduz um pedido em linguagem natural ("constrói-me o reator") na forma
geométrica que o HUD sabe desenhar em wireframe.
"""
from __future__ import annotations

# Formas que o motor 3D do HUD sabe renderizar.
FORMAS = {"reator", "esfera", "toroide", "cilindro", "estrutura", "capacete", "manopla"}

# Sinónimos / peças -> forma geométrica.
PECA_FORMA = {
    "reator": "reator", "arc reactor": "reator", "reator arc": "reator", "nucleo de energia": "reator",
    "capacete": "capacete", "helmet": "capacete", "mascara": "capacete", "elmo": "capacete",
    "manopla": "manopla", "luva": "manopla", "gauntlet": "manopla", "braco": "manopla",
    "esfera": "esfera", "nucleo": "esfera", "core": "esfera", "bola": "esfera",
    "toroide": "toroide", "anel": "toroide", "aro": "toroide",
    "estrutura": "estrutura", "chassis": "estrutura", "cubo": "estrutura", "grelha": "estrutura",
    "cilindro": "cilindro", "motor": "cilindro", "turbina": "cilindro",
}


def _num(valor, minimo, maximo, omissao):
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return omissao
    return max(minimo, min(maximo, v))


def _resolver_forma(peca: str | None, forma: str | None) -> str:
    p = (peca or "").lower().strip()
    f = (forma or "").lower().strip()
    if f in FORMAS:
        return f
    if p in PECA_FORMA:
        return PECA_FORMA[p]
    for chave, valor in PECA_FORMA.items():
        if chave in p:
            return valor
    return "reator"


def plan_model(peca=None, forma=None, cor=None, tamanho=None, segmentos=None, rot=None) -> dict:
    """Planeia um modelo 3D paramétrico -> {peca, forma, cor, escala, segmentos, rot}."""
    f = _resolver_forma(peca, forma)
    r = [0.0, 0.0, 0.0]
    if isinstance(rot, (list, tuple)) and len(rot) == 3:
        try:
            r = [float(rot[0]), float(rot[1]), float(rot[2])]
        except (TypeError, ValueError):
            r = [0.0, 0.0, 0.0]
    return {
        "peca": peca or f,
        "forma": f,
        "cor": cor or "#35e6ff",
        "escala": _num(tamanho, 0.2, 3.0, 1.0),
        "segmentos": int(_num(segmentos, 6, 48, 0)),  # 0 = usar valor por defeito
        "rot": r,
    }


def plan_scene(partes) -> dict:
    """Planeia uma cena composta por várias peças posicionadas no espaço.

    `partes` é uma lista de dicionários, cada um com forma/peca e, opcionalmente,
    cor, tamanho, segmentos e pos ([x, y, z]).
    """
    if not isinstance(partes, list):
        return {"erro": "partes deve ser uma lista"}
    out = []
    for parte in partes[:12]:
        if not isinstance(parte, dict):
            continue
        m = plan_model(
            parte.get("peca"), parte.get("forma"), parte.get("cor"),
            parte.get("tamanho") or parte.get("escala"), parte.get("segmentos"),
            parte.get("rot"),
        )
        pos = parte.get("pos") or [0, 0, 0]
        try:
            m["pos"] = [_num(pos[0], -3, 3, 0), _num(pos[1], -3, 3, 0), _num(pos[2], -3, 3, 0)]
        except (TypeError, IndexError):
            m["pos"] = [0, 0, 0]
        out.append(m)
    return {"partes": out}
