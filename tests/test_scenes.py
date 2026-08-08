from jarvis.scenes import SceneStore, get_store
from jarvis.actions import ActionSink
from jarvis.tools import build_default_registry


def test_scene_store_guardar_carregar():
    store = SceneStore()
    partes = [
        {"forma": "esfera", "pos": [1, 0, 0], "cor": "#35e6ff"},
        {"forma": "cilindro", "pos": [-1, 0, 0], "tamanho": 0.5},
    ]
    res = store.guardar("teste_cena_unit", partes)
    assert res["ok"] and res["pecas"] == 2

    carregado = store.carregar("teste_cena_unit")
    assert carregado["ok"]
    assert len(carregado["partes"]) == 2
    assert carregado["partes"][0]["forma"] == "esfera"
    assert "teste_cena_unit" in store.listar()


def test_scene_store_guardar_vazio():
    store = SceneStore()
    assert "erro" in store.guardar("vazio", [])


def test_scene_store_carregar_inexistente():
    store = SceneStore()
    assert "erro" in store.carregar("nao-existe-xyz-123")


def test_definir_atual_e_guardar():
    store = SceneStore()
    store.definir_atual([{"forma": "reator", "pos": [0, 0, 0]}])
    res = store.guardar("teste_atual_unit")
    assert res["ok"] and res["pecas"] == 1


def test_ferramentas_de_projeto_registadas():
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    for nome in ["guardar_projeto", "carregar_projeto", "listar_projetos"]:
        assert nome in reg.names()


def test_carregar_projeto_gera_acao_cena():
    sink = ActionSink()
    reg = build_default_registry(memory=None, allow_shell=False, actions=sink)
    get_store().guardar("teste_acao_unit", [{"forma": "esfera", "pos": [0, 0, 0]}])
    reg.call("carregar_projeto", {"nome": "teste_acao_unit"})
    tipos = [a["tipo"] for a in sink.items]
    assert "cena" in tipos
