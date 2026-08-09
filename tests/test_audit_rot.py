from jarvis.actions import ActionSink
from jarvis.scenes import SceneStore
from jarvis.tools import build_default_registry
from jarvis.tools.holo import plan_model, plan_scene


def test_plan_model_rotacao():
    m = plan_model("esfera", rot=[0.5, 1.0, 0.2])
    assert m["rot"] == [0.5, 1.0, 0.2]


def test_plan_model_rot_default():
    assert plan_model("reator")["rot"] == [0.0, 0.0, 0.0]


def test_plan_scene_preserva_escala_e_rot():
    cena = plan_scene([{"forma": "cilindro", "escala": 0.5, "rot": [0, 1.5, 0], "pos": [1, 0, 0]}])
    parte = cena["partes"][0]
    assert parte["escala"] == 0.5
    assert parte["rot"] == [0, 1.5, 0]


def test_scene_roundtrip_escala_rot():
    store = SceneStore()
    store.guardar("teste_rot_unit", [{"forma": "esfera", "escala": 2.0,
                                      "rot": [0.3, 0.6, 0.9], "pos": [0, 1, 0]}])
    try:
        carregado = store.carregar("teste_rot_unit")
        p = carregado["partes"][0]
        assert p["escala"] == 2.0
        assert p["rot"] == [0.3, 0.6, 0.9]
    finally:
        store.apagar("teste_rot_unit")


def test_auditoria_ferramenta_registada_e_gera_painel():
    sink = ActionSink()
    reg = build_default_registry(memory=None, allow_shell=False, actions=sink)
    assert "auditoria_seguranca" in reg.names()
    reg.call("auditoria_seguranca", {})
    paineis = [a for a in sink.items if a["tipo"] == "painel"]
    assert paineis and "Auditoria" in paineis[0]["titulo"]
    assert "Recomendações" in paineis[0]["texto"]


def test_escrever_codigo_gera_acao_codigo():
    from jarvis.config import WORKSPACE_DIR
    sink = ActionSink()
    reg = build_default_registry(memory=None, allow_shell=False, actions=sink)
    try:
        reg.call("escrever_codigo", {"nome": "t_cod_acao", "linguagem": "python",
                                     "codigo": "print(1)\n"})
        assert any(a["tipo"] == "codigo" for a in sink.items)
    finally:
        (WORKSPACE_DIR / "t_cod_acao.py").unlink(missing_ok=True)
