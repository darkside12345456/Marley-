from jarvis.setup import _tem_modelo


def test_reconhece_modelo_com_tag():
    # o Ollama lista modelos como 'llama3.1:latest'
    assert _tem_modelo(["llama3.1:latest", "qwen2.5:7b"], "llama3.1")
    assert _tem_modelo(["llama3.1:latest"], "llama3.1:latest")


def test_reconhece_modelo_base():
    assert _tem_modelo(["qwen2.5-coder:latest"], "qwen2.5-coder")


def test_modelo_em_falta():
    assert not _tem_modelo(["mistral:latest"], "llama3.1")
    assert not _tem_modelo([], "llama3.1")
