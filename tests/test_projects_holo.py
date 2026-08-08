import shutil

from jarvis.actions import ActionSink
from jarvis.config import WORKSPACE_DIR
from jarvis.tools import build_default_registry
from jarvis.tools.holo import plan_model, plan_scene
from jarvis.tools.projects import criar_projeto


def test_plan_model_parametros():
    m = plan_model("esfera", tamanho=2.5, segmentos=30)
    assert m["forma"] == "esfera"
    assert m["escala"] == 2.5
    assert m["segmentos"] == 30


def test_plan_model_limites():
    m = plan_model("reator", tamanho=99, segmentos=999)
    assert m["escala"] == 3.0        # limitado a 3
    assert m["segmentos"] == 48       # limitado a 48


def test_plan_scene():
    cena = plan_scene([
        {"forma": "esfera", "pos": [1, 0, 0]},
        {"forma": "cilindro", "pos": [-1, 0, 0], "tamanho": 0.5},
    ])
    assert len(cena["partes"]) == 2
    assert cena["partes"][0]["pos"] == [1, 0, 0]


def test_plan_scene_input_invalido():
    assert "erro" in plan_scene("não é lista")


def test_criar_projeto_web():
    nome = "teste-jarvis-xyz"
    try:
        out = criar_projeto(nome, "web", "app de teste")
        assert out["ok"] is True
        pasta = WORKSPACE_DIR / out["pasta"]
        assert (pasta / "index.html").is_file()
        assert (pasta / "app.js").is_file()
        assert out["abrir_url"].endswith("/index.html")
    finally:
        shutil.rmtree(WORKSPACE_DIR / "teste-jarvis-xyz", ignore_errors=True)


def test_criar_projeto_tipo_invalido():
    out = criar_projeto("x", "cobol")
    assert "erro" in out


def test_registry_tem_novas_ferramentas():
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    for nome in ["construir_modelo", "construir_cena", "verificar_ameacas",
                 "analisar_processos", "analisar_rede", "analisar_ficheiros",
                 "calcular_hash", "criar_projeto", "abrir_pagina"]:
        assert nome in reg.names()
