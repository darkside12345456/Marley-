import json

from jarvis.actions import ActionSink
from jarvis.tools import build_default_registry
from jarvis.tools.browser import normalizar_url
from jarvis.tools.holo import plan_model


def test_normalizar_url_completo():
    assert normalizar_url("https://exemplo.com")["url"] == "https://exemplo.com"


def test_normalizar_url_dominio():
    out = normalizar_url("youtube.com")
    assert out["url"] == "https://youtube.com"
    assert out["pesquisa"] is False


def test_normalizar_url_pesquisa():
    out = normalizar_url("notícias de hoje")
    assert "google.com/search" in out["url"]
    assert out["pesquisa"] is True


def test_plan_model_por_sinonimo():
    assert plan_model("arc reactor")["forma"] == "reator"
    assert plan_model("capacete")["forma"] == "capacete"
    assert plan_model("luva")["forma"] == "manopla"


def test_plan_model_forma_desconhecida_cai_em_reator():
    assert plan_model("coisa estranha")["forma"] == "reator"


def test_plan_model_cor_default():
    assert plan_model("esfera")["cor"] == "#35e6ff"


def test_abrir_pagina_gera_acao():
    sink = ActionSink()
    reg = build_default_registry(memory=None, allow_shell=False, actions=sink)
    reg.call("abrir_pagina", {"alvo": "youtube.com"})
    assert sink.items[0]["tipo"] == "abrir_pagina"
    assert sink.items[0]["url"] == "https://youtube.com"


def test_construir_modelo_gera_acao():
    sink = ActionSink()
    reg = build_default_registry(memory=None, allow_shell=False, actions=sink)
    reg.call("construir_modelo", {"peca": "reator"})
    assert sink.items[0]["tipo"] == "modelo"
    assert sink.items[0]["forma"] == "reator"


def test_ui_tools_ausentes_sem_sink():
    reg = build_default_registry(memory=None, allow_shell=False, actions=None)
    assert "abrir_pagina" not in reg.names()
    assert "construir_modelo" not in reg.names()


def test_drain_limpa():
    sink = ActionSink()
    sink.add("x")
    assert sink.drain() == [{"tipo": "x"}]
    assert sink.items == []
