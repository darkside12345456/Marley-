import shutil

from jarvis import mesh
from jarvis.config import WORKSPACE_DIR
from jarvis.scheduler import SecurityScheduler
from jarvis.tools.projects import criar_projeto


def test_gerar_obj_esfera_tem_faces():
    obj = mesh.gerar_obj("esfera", 1.0, 16)
    assert obj.startswith("# Exportado pelo Jarvis")
    assert "\nv " in obj
    assert "\nf " in obj  # sólido -> tem faces


def test_gerar_obj_reator_tem_linhas():
    obj = mesh.gerar_obj("reator", 1.0)
    assert "\nl " in obj  # reator é wireframe -> linhas


def test_gerar_obj_escala():
    pequeno = mesh.gerar_obj("estrutura", 0.5)
    grande = mesh.gerar_obj("estrutura", 2.0)
    assert "2.00000" in grande and "0.50000" in pequeno


def test_exportar_obj_cria_ficheiro():
    destino = WORKSPACE_DIR / "teste_export.obj"
    try:
        mesh.exportar_obj("cilindro", destino, 1.0, 20)
        assert destino.is_file()
        assert destino.read_text().count("v ") > 10
    finally:
        destino.unlink(missing_ok=True)


def test_scheduler_executar_e_estado():
    sch = SecurityScheduler()
    res = sch.executar_agora()
    assert res["nivel"] in {"BAIXO", "MÉDIO", "ALTO"}
    estado = sch.estado()
    assert estado["ativo"] is False
    assert estado["ultima"]["nivel"] == res["nivel"]


def test_scheduler_iniciar_parar():
    sch = SecurityScheduler()
    estado = sch.iniciar(0)  # 0 = desligado
    assert estado["ativo"] is False
    sch.parar()


def test_criar_projeto_react_e_api():
    for tipo, marca in [("react", "app.jsx"), ("api", "app.py")]:
        nome = f"teste-{tipo}-xyz"
        try:
            out = criar_projeto(nome, tipo)
            assert out["ok"] is True
            assert marca in out["ficheiros"]
        finally:
            shutil.rmtree(WORKSPACE_DIR / nome, ignore_errors=True)
