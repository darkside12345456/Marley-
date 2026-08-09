from jarvis.tools import news
from jarvis.tools.news import CATEGORIAS, obter_noticias

_RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item>
    <title>Nova descoberta em IA revoluciona a medicina - Público</title>
    <link>https://exemplo.pt/a</link>
    <pubDate>Mon, 09 Aug 2026 08:00:00 GMT</pubDate>
    <source url="https://publico.pt">Público</source>
  </item>
  <item>
    <title>Mercados sobem após anúncio - Observador</title>
    <link>https://exemplo.pt/b</link>
    <pubDate>Mon, 09 Aug 2026 07:30:00 GMT</pubDate>
  </item>
</channel></rss>"""


def test_parsing_noticias(monkeypatch):
    monkeypatch.setattr(news, "_fetch", lambda url: _RSS.encode("utf-8"))
    r = obter_noticias("tecnologia", 5)
    assert "noticias" in r and len(r["noticias"]) == 2
    n0 = r["noticias"][0]
    assert n0["titulo"] == "Nova descoberta em IA revoluciona a medicina"
    assert n0["fonte"] == "Público"
    assert n0["link"] == "https://exemplo.pt/a"
    # sem <source>, extrai a fonte do sufixo do título
    assert r["noticias"][1]["fonte"] == "Observador"


def test_limite_respeitado(monkeypatch):
    monkeypatch.setattr(news, "_fetch", lambda url: _RSS.encode("utf-8"))
    assert len(obter_noticias("mundo", 1)["noticias"]) == 1


def test_categorias_mapeiam_pesquisa(monkeypatch):
    monkeypatch.setattr(news, "_fetch", lambda url: _RSS.encode("utf-8"))
    r = obter_noticias("ia")
    assert r["tema"] == "inteligência artificial"  # atalho 'ia'
    assert "ia" in CATEGORIAS


def test_erro_sem_rede(monkeypatch):
    def _boom(url):
        raise OSError("sem rede")
    monkeypatch.setattr(news, "_fetch", _boom)
    r = obter_noticias("mundo")
    assert "erro" in r


def test_ferramenta_registada():
    from jarvis.actions import ActionSink
    from jarvis.tools import build_default_registry
    reg = build_default_registry(memory=None, allow_shell=False, actions=ActionSink())
    assert "obter_noticias" in reg.names()
