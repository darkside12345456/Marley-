from jarvis.assistant import Assistant
from jarvis.config import config
from jarvis.web.server import create_app


def _client():
    return create_app(Assistant(config)).test_client()


def test_bloqueia_post_de_outra_origem():
    c = _client()
    r = c.post("/api/scene/current", json={"partes": []},
               headers={"Origin": "http://sitemalicioso.com"})
    assert r.status_code == 403


def test_permite_post_mesma_origem():
    c = _client()
    r = c.post("/api/scene/current", json={"partes": []},
               headers={"Origin": "http://localhost"})
    # mesma origem (host do pedido de teste é 'localhost')
    assert r.status_code == 200


def test_permite_post_sem_origem():
    # ferramentas/CLI não enviam Origin -> permitido
    c = _client()
    assert c.post("/api/scene/current", json={"partes": []}).status_code == 200


def test_get_nao_e_bloqueado_por_origem():
    c = _client()
    assert c.get("/api/status", headers={"Origin": "http://x.com"}).status_code == 200


def test_export_sanitiza_nome_ficheiro():
    c = _client()
    r = c.get('/api/export/rea"tor')
    cd = r.headers.get("Content-Disposition", "")
    assert '"' not in cd.replace('filename="', "").replace('.obj"', "")
