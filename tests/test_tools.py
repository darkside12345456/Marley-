import json

from jarvis.tools import build_default_registry
from jarvis.tools.basics import current_time


def test_registry_has_expected_tools():
    reg = build_default_registry(memory=None, allow_shell=False)
    nomes = reg.names()
    for esperado in ["obter_hora", "obter_meteorologia", "pesquisar_web",
                     "ler_ficheiro", "escrever_ficheiro", "executar_comando"]:
        assert esperado in nomes


def test_schemas_are_valid():
    reg = build_default_registry(memory=None, allow_shell=False)
    for s in reg.schemas():
        assert s["type"] == "function"
        assert "name" in s["function"]
        assert "parameters" in s["function"]


def test_current_time_tool():
    reg = build_default_registry(memory=None, allow_shell=False)
    out = reg.call("obter_hora", {})
    assert "/" in out  # data no formato dd/mm/aaaa


def test_shell_disabled_by_default():
    reg = build_default_registry(memory=None, allow_shell=False)
    out = json.loads(reg.call("executar_comando", {"comando": "echo oi"}))
    assert "erro" in out


def test_unknown_tool_returns_error():
    reg = build_default_registry(memory=None, allow_shell=False)
    out = json.loads(reg.call("inexistente", {}))
    assert "error" in out
