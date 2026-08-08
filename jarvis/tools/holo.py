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


def plan_model(peca: str | None = None, forma: str | None = None, cor: str | None = None) -> dict:
    """Devolve {peca, forma, cor} pronto a enviar ao HUD."""
    p = (peca or "").lower().strip()
    f = (forma or "").lower().strip()

    if f not in FORMAS:
        f = PECA_FORMA.get(p, "")
    if not f:
        # tenta encontrar uma palavra-chave dentro do texto da peça
        for chave, valor in PECA_FORMA.items():
            if chave in p:
                f = valor
                break
    if f not in FORMAS:
        f = "reator"

    return {"peca": peca or f, "forma": f, "cor": cor or "#35e6ff"}
