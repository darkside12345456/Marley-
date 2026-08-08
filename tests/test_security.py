import tempfile
from pathlib import Path

from jarvis import security


def test_verificar_ameacas_estrutura():
    rel = security.verificar_ameacas()
    assert rel["nivel"] in {"BAIXO", "MÉDIO", "ALTO"}
    assert isinstance(rel["relatorio"], str) and rel["relatorio"]
    assert "aviso" in rel  # nunca esquece o aviso de que não substitui antivírus


def test_analisar_processos_nao_rebenta():
    out = security.analisar_processos(limite=20)
    # devolve suspeitos ou indica não-suportado, mas nunca lança exceção
    assert "suspeitos" in out or out.get("suportado") is False


def test_analisar_ficheiros_deteta_dupla_extensao():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "fatura.pdf.exe").write_text("x")
        (Path(d) / "normal.txt").write_text("ok")
        out = security.analisar_ficheiros(d)
        nomes = [s["ficheiro"] for s in out["suspeitos"]]
        assert any("fatura.pdf.exe" in n for n in nomes)


def test_calcular_hash():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "a.txt"
        f.write_text("abc")
        out = security.calcular_hash(str(f))
        # sha256("abc")
        assert out["sha256"] == (
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        )


def test_analisar_ficheiros_caminho_inexistente():
    out = security.analisar_ficheiros("/caminho/que/nao/existe/xyz")
    assert "erro" in out
