from jarvis import meta as meta_mod
from jarvis.assistant import Assistant
from jarvis.config import config
from jarvis.web.server import create_app


def test_meta_roundtrip_e_percent():
    meta_mod.set_meta(atual=0)
    try:
        m = meta_mod.set_meta(atual=25000, alvo=100000)
        assert m["atual"] == 25000 and m["alvo"] == 100000
        assert m["percent"] == 25.0
    finally:
        meta_mod.set_meta(atual=0)


def test_meta_percent_limitado():
    try:
        assert meta_mod.set_meta(atual=999999, alvo=100000)["percent"] == 100.0
    finally:
        meta_mod.set_meta(atual=0)


def test_endpoint_meta_get_post():
    c = create_app(Assistant(config)).test_client()
    try:
        assert c.post("/api/meta", json={"atual": 5000}).get_json()["atual"] == 5000
        assert c.get("/api/meta").get_json()["atual"] == 5000
    finally:
        meta_mod.set_meta(atual=0)


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
