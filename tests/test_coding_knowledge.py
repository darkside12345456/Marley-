from jarvis import knowledge
from jarvis.actions import ActionSink
from jarvis.config import WORKSPACE_DIR
from jarvis.scenes import SceneStore
from jarvis.tools import build_default_registry
from jarvis.tools.coding import extensao, guardar_codigo


def test_extensao_varias_linguagens():
    assert extensao("python") == "py"
    assert extensao("Rust") == "rs"
    assert extensao("c++") == "cpp"
    assert extensao("linguagem-desconhecida") == "txt"


def test_guardar_codigo_cria_ficheiro():
    res = guardar_codigo("teste_cod_unit", "python", "print('oi')\n")
    try:
        assert res["ok"]
        assert res["ficheiro"].endswith("teste_cod_unit.py")
        assert (WORKSPACE_DIR / "teste_cod_unit.py").is_file()
    finally:
        (WORKSPACE_DIR / "teste_cod_unit.py").unlink(missing_ok=True)


def test_guardar_codigo_fora_da_sandbox():
    res = guardar_codigo("../fora", "python", "x")
    # o slug remove o traço inicial; garante que fica dentro da workspace
    assert res.get("ok") or "erro" in res
    if res.get("ok"):
        assert "workspace/" in res["ficheiro"]
        from pathlib import Path
        Path(WORKSPACE_DIR / res["ficheiro"].split("workspace/")[-1]).unlink(missing_ok=True)


def test_knowledge_consulta_direta():
    r = knowledge.consultar("phishing")
    assert r["topico"] == "phishing"
    assert "urgência" in r["conselho"] or "link" in r["conselho"].lower()


def test_knowledge_sem_topico_lista():
    r = knowledge.consultar("")
    assert "topicos" in r and "ransomware" in r["topicos"]


def test_knowledge_desconhecido_sugere():
    r = knowledge.consultar("xpto-nao-existe")
    assert r["conselho"] is None
    assert "sugestoes" in r


def test_scenes_apagar_e_renomear():
    store = SceneStore()
    store.guardar("proj_orig_unit", [{"forma": "esfera", "pos": [0, 0, 0]}])
    r = store.renomear("proj_orig_unit", "proj_novo_unit")
    assert r["ok"]
    assert "proj_novo_unit" in store.listar()
    assert "proj_orig_unit" not in store.listar()
    assert store.apagar("proj_novo_unit")["ok"]
    assert "proj_novo_unit" not in store.listar()


def test_registry_novas_ferramentas():
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    for nome in ["escrever_codigo", "consultar_seguranca", "listar_topicos_seguranca",
                 "apagar_projeto", "renomear_projeto"]:
        assert nome in reg.names()
