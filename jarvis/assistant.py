"""O orquestrador do Jarvis: junta cérebro + memória + ferramentas."""
from __future__ import annotations

from datetime import datetime

from .actions import ActionSink
from .brain import Brain
from .config import Config
from .memory import Memory
from .tools import build_default_registry

# Nomes amigáveis das ferramentas para o relatório de atividade.
_ACAO_LABEL = {
    "obter_noticias": "Consultou notícias", "obter_meteorologia": "Verificou a meteorologia",
    "pesquisar_web": "Pesquisou na web", "verificar_ameacas": "Verificou ameaças",
    "auditoria_seguranca": "Fez uma auditoria de segurança", "escrever_codigo": "Escreveu código",
    "criar_projeto": "Criou uma aplicação", "construir_modelo": "Projetou uma peça 3D",
    "construir_cena": "Montou uma cena 3D", "exportar_modelo": "Exportou um modelo",
    "exportar_cena": "Exportou uma cena", "abrir_pagina": "Abriu uma página",
    "escrever_ficheiro": "Escreveu um ficheiro", "ler_ficheiro": "Leu um ficheiro",
    "memorizar": "Guardou um facto", "guardar_projeto": "Guardou um projeto 3D",
    "carregar_projeto": "Carregou um projeto 3D", "consultar_seguranca": "Deu conselhos de segurança",
    "executar_comando": "Pediu um comando do sistema",
}


class Assistant:
    def __init__(self, config: Config):
        self.config = config
        self.brain = Brain(config.ollama_host, config.model, config.temperature)
        self.memory = Memory(config.db_path)
        self.actions = ActionSink()
        self.last_actions: list[dict] = []
        self.activity: list[dict] = []  # relatório de atividade da sessão
        self.tools = build_default_registry(self.memory, config.allow_shell, self.actions,
                                            config.confirm_shell)

    def _registar_atividade(self, ferramenta: str) -> None:
        self.activity.append({
            "ts": datetime.now().strftime("%H:%M"),
            "ferramenta": ferramenta,
            "resumo": _ACAO_LABEL.get(ferramenta, ferramenta.replace("_", " ")),
        })
        if len(self.activity) > 100:
            self.activity = self.activity[-100:]

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
        self.actions.clear()

        # Resposta direta e fiável (horas, tempo, data, notícias) — não depende
        # do modelo, por isso é instantânea mesmo com um modelo local lento.
        from . import intents
        try:
            direto = intents.responder(user_text)
        except Exception:  # noqa: BLE001
            direto = None
        if direto is not None:
            self.memory.add_message("assistant", direto)
            self._registar_atividade("resposta_direta")
            self.last_actions = self.actions.drain()
            return direto

        messages = self._base_messages()

        for _ in range(max_tool_rounds):
            msg = self.brain.chat(messages, tools=self.tools.schemas())
            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                answer = (msg.get("content") or "").strip()
                self.memory.add_message("assistant", answer)
                self.last_actions = self.actions.drain()
                return answer

            messages.append(msg)
            for call in tool_calls:
                fn = call.get("function", {})
                name = fn.get("name", "")
                args = fn.get("arguments", {})
                result = self.tools.call(name, args)
                self._registar_atividade(name)
                messages.append({"role": "tool", "name": name, "content": result})

        # Se esgotou as voltas, faz uma resposta final sem ferramentas.
        final = self.brain.chat(messages)
        answer = (final.get("content") or "").strip()
        self.memory.add_message("assistant", answer)
        self.last_actions = self.actions.drain()
        return answer

    def reset(self) -> None:
        self.memory.clear_messages()

    def close(self) -> None:
        self.memory.close()
