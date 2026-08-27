from jarvis.assistant import Assistant
from jarvis.config import config
from jarvis.web.server import create_app


def test_modules_endpoint():
    c = create_app(Assistant(config)).test_client()
    nomes = [m["nome"] for m in c.get("/api/modules").get_json()["modulos"]]
    assert "CÉREBRO" in nomes and "SEGURANÇA" in nomes


def test_activity_endpoint_vazio():
    c = create_app(Assistant(config)).test_client()
    assert c.get("/api/activity").get_json() == {"atividade": []}


def test_atividade_registada_apos_ferramenta():
    class Fake:
        def __init__(self): self.i = 0
        def is_available(self): return True
        def chat(self, m, tools=None):
            self.i += 1
            if self.i == 1:
                return {"role": "assistant", "content": "",
                        "tool_calls": [{"function": {"name": "obter_hora", "arguments": {}}}]}
            return {"role": "assistant", "content": "São horas."}
    a = Assistant(config)
    a.brain = Fake()
    a.ask("que horas são?")
    assert a.activity and a.activity[-1]["ferramenta"] == "obter_hora"
    a.close()
