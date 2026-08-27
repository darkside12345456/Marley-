from jarvis.brain import Brain


def _brain(modelo, tags):
    b = Brain("http://localhost:11434", modelo)
    b.modelos_disponiveis = lambda: tags  # simula o que o Ollama tem
    return b


def test_resolve_para_etiqueta_instalada():
    # pediste 'llama3.1' mas só tens 'llama3.1:8b'
    b = _brain("llama3.1", ["llama3:latest", "llama3.1:8b"])
    assert b.resolver_modelo() == "llama3.1:8b"
    assert b.model == "llama3.1:8b"


def test_mantem_se_ja_existe_exato():
    b = _brain("llama3.1:8b", ["llama3.1:8b"])
    assert b.resolver_modelo() == "llama3.1:8b"


def test_mantem_se_ha_latest():
    b = _brain("llama3", ["llama3:latest"])
    assert b.resolver_modelo() == "llama3"  # o Ollama resolve o :latest


def test_mantem_se_nada_bate():
    b = _brain("mistral", ["llama3.1:8b"])
    assert b.resolver_modelo() == "mistral"


def test_sem_servidor_nao_altera():
    b = _brain("llama3.1", [])
    assert b.resolver_modelo() == "llama3.1"
