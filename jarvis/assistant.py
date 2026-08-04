"""O orquestrador do Jarvis: junta cérebro + memória + ferramentas."""
from __future__ import annotations

from .brain import Brain
from .config import Config
from .memory import Memory
from .tools import build_default_registry


class Assistant:
    def __init__(self, config: Config):
        self.config = config
        self.brain = Brain(config.ollama_host, config.model, config.temperature)
        self.memory = Memory(config.db_path)
        self.tools = build_default_registry(self.memory, config.allow_shell)

    def _base_messages(self) -> list[dict]:
        system = self.config.system_prompt()
        facts = self.memory.facts_summary()
        if facts:
            system += "\n\n" + facts
        msgs = [{"role": "system", "content": system}]
        msgs += self.memory.recent_messages(self.config.max_history)
        return msgs

    def ask(self, user_text: str, max_tool_rounds: int = 5) -> str:
        """Pergunta com ciclo de ferramentas. Devolve a resposta final em texto."""
        self.memory.add_message("user", user_text)
        messages = self._base_messages()

        for _ in range(max_tool_rounds):
            msg = self.brain.chat(messages, tools=self.tools.schemas())
            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                answer = (msg.get("content") or "").strip()
                self.memory.add_message("assistant", answer)
                return answer

            messages.append(msg)
            for call in tool_calls:
                fn = call.get("function", {})
                name = fn.get("name", "")
                args = fn.get("arguments", {})
                result = self.tools.call(name, args)
                messages.append({"role": "tool", "name": name, "content": result})

        # Se esgotou as voltas, faz uma resposta final sem ferramentas.
        final = self.brain.chat(messages)
        answer = (final.get("content") or "").strip()
        self.memory.add_message("assistant", answer)
        return answer

    def reset(self) -> None:
        self.memory.clear_messages()

    def close(self) -> None:
        self.memory.close()
