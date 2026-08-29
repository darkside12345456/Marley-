from jarvis import intents
from jarvis.tools import basics, news, weather, web


def test_extrair_local():
    assert intents._local("tempo em lisboa") == "lisboa"
    assert intents._local("que horas são em tóquio") == "tóquio"
    assert intents._local("que horas são") == ""


def test_horas_local_sem_rede():
    # a hora local não precisa de Internet
    r = intents.responder("que horas são")
    assert r and "São" in r and ":" in r


def test_data():
    r = intents.responder("que dia é hoje?")
    assert r and "Hoje é" in r


def test_tempo_com_cidade(monkeypatch):
    monkeypatch.setattr(weather, "get_weather", lambda local: {
        "local": "Lisboa, Portugal", "condicao": "céu limpo", "temperatura_c": 25,
        "sensacao_c": 26, "max_c": 28, "min_c": 18, "vento_kmh": 10, "humidade_pct": 40})
    r = intents.responder("como está o tempo em Lisboa?")
    assert "Lisboa" in r and "25" in r and "céu limpo" in r


def test_tempo_sem_cidade_pergunta():
    r = intents.responder("está calor?")
    assert "De que cidade" in r


def test_horas_de_cidade(monkeypatch):
    def fake(local=""):
        if local:
            return {"local": "Tóquio, Japão", "hora": "20:11",
                    "data": "27/08/2026", "dia_semana": "quarta-feira"}
        return {"local": "aqui", "hora": "12:00", "data": "x", "dia_semana": "y"}
    monkeypatch.setattr(basics, "current_time", fake)
    r = intents.responder("que horas são em Tóquio")
    assert "Tóquio" in r and "20:11" in r


def test_noticias(monkeypatch):
    monkeypatch.setattr(news, "obter_noticias",
                        lambda tema="", limite=6: {"tema": "tecnologia",
                                                   "noticias": [{"titulo": "Nova IA", "fonte": "Público"}]})
    r = intents.responder("dá-me as últimas notícias de tecnologia")
    assert "Últimas notícias" in r and "Nova IA" in r


def test_pesquisa_web(monkeypatch):
    monkeypatch.setattr(web, "web_search", lambda consulta: {
        "consulta": consulta,
        "resultados": [{"resumo": "É uma técnica de aprendizagem automática.", "fonte": "Wikipédia"}]})
    r = intents.responder("o que é machine learning?")
    assert r and "aprendizagem automática" in r
    r2 = intents.responder("pesquisa energia solar")
    assert r2 and "aprendizagem" in r2  # (mesma resposta simulada)


def test_conversa_normal_nao_e_intercetada():
    assert intents.responder("olá, tudo bem?") is None
    assert intents.responder("escreve-me um poema") is None
    assert intents.responder("") is None
