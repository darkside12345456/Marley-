from jarvis import mesh
from jarvis.actions import ActionSink
from jarvis.scenes import get_store
from jarvis.scheduler import SecurityScheduler
from jarvis.tools import build_default_registry


def test_gerar_obj_cena_combina_pecas():
    partes = [
        {"forma": "esfera", "escala": 1, "pos": [2, 0, 0], "rot": [0, 0, 0]},
        {"forma": "estrutura", "escala": 1, "pos": [-2, 0, 0], "rot": [0, 0.5, 0]},
    ]
    obj = mesh.gerar_obj_cena(partes)
    assert obj.count("\no ") == 2           # dois objetos
    assert "\nf " in obj                     # faces (sólido)
    # a esfera está deslocada em +2 no X -> deve haver vértices > 2.5
    xs = [float(l.split()[1]) for l in obj.splitlines() if l.startswith("v ")]
    assert max(xs) > 2.5


def test_gerar_obj_cena_vazia():
    obj = mesh.gerar_obj_cena([])
    assert "Cena exportada" in obj


def test_scheduler_historico():
    sch = SecurityScheduler()
    sch.registar({"nivel": "BAIXO", "processos": {"suspeitos": []}, "rede": {"alertas": []}})
    hist = sch.historico()
    assert hist and hist[-1]["nivel"] == "BAIXO"
    assert "ts" in hist[-1]


def test_ferramentas_registadas():
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    for nome in ["exportar_cena", "historico_seguranca", "auditoria_seguranca"]:
        assert nome in reg.names()


def test_exportar_cena_ferramenta():
    from jarvis.config import WORKSPACE_DIR
    get_store().definir_atual([{"forma": "reator", "pos": [0, 0, 0]}])
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    try:
        res = reg.call("exportar_cena", {"nome": "teste_cena_exp"})
        import json
        d = json.loads(res)
        assert d["ok"] and (WORKSPACE_DIR / "teste_cena_exp.obj").is_file()
    finally:
        (WORKSPACE_DIR / "teste_cena_exp.obj").unlink(missing_ok=True)
