import tempfile
from pathlib import Path

from jarvis.memory import Memory


def test_messages_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        mem = Memory(Path(d) / "t.db")
        mem.add_message("user", "olá")
        mem.add_message("assistant", "bom dia")
        msgs = mem.recent_messages()
        assert [m["role"] for m in msgs] == ["user", "assistant"]
        assert msgs[0]["content"] == "olá"
        mem.close()


def test_facts_upsert_and_recall():
    with tempfile.TemporaryDirectory() as d:
        mem = Memory(Path(d) / "t.db")
        mem.remember("nome", "Joana")
        mem.remember("nome", "Joana Pinto")  # atualiza
        factos = mem.recall("nome")
        assert len(factos) == 1
        assert factos[0]["value"] == "Joana Pinto"
        assert "nome: Joana Pinto" in mem.facts_summary()
        mem.close()


def test_clear_messages():
    with tempfile.TemporaryDirectory() as d:
        mem = Memory(Path(d) / "t.db")
        mem.add_message("user", "x")
        mem.clear_messages()
        assert mem.recent_messages() == []
        mem.close()
