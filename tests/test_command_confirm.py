import json

from jarvis.actions import ActionSink
from jarvis.commands import PendingCommands, get_pending
from jarvis.tools import build_default_registry


def test_pending_add_pop_unico():
    p = PendingCommands()
    cid = p.add("echo oi")
    assert p.pop(cid) == "echo oi"
    assert p.pop(cid) is None            # só pode ser usado uma vez


def test_shell_desligado_continua_bloqueado():
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    out = json.loads(reg.call("executar_comando", {"comando": "echo oi"}))
    assert "erro" in out and "desativados" in out["erro"].lower()


def test_shell_ligado_pede_confirmacao():
    sink = ActionSink()
    reg = build_default_registry(memory=None, allow_shell=True, actions=sink, confirm_shell=True)
    out = json.loads(reg.call("executar_comando", {"comando": "echo oi"}))
    assert out.get("pendente") is True
    # gerou uma ação de confirmação com id + comando
    acao = [a for a in sink.items if a["tipo"] == "confirmar_comando"]
    assert acao and acao[0]["comando"] == "echo oi" and acao[0]["id"]
    # o comando ficou pendente (não executado)
    assert get_pending().pop(acao[0]["id"]) == "echo oi"


def test_shell_ligado_sem_confirmacao_executa():
    reg = build_default_registry(memory=None, allow_shell=True, actions=ActionSink(),
                                 confirm_shell=False)
    out = json.loads(reg.call("executar_comando", {"comando": "echo confirmado"}))
    assert out.get("codigo") == 0
    assert "confirmado" in (out.get("saida") or "")


def test_endpoint_so_corre_pendentes():
    from jarvis.assistant import Assistant
    from jarvis.config import config
    from jarvis.web.server import create_app
    a = Assistant(config)
    c = create_app(a).test_client()
    # id inexistente -> 404 (se a shell estiver ligada) ou 403 (se desligada)
    r = c.post("/api/command/run", json={"id": "inexistente123"})
    assert r.status_code in (403, 404)
    a.close()
