"""Registo de ferramentas: mapeia nomes -> função + esquema JSON."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from . import weather as weather_mod
from . import web as web_mod
from . import files as files_mod
from . import system as system_mod
from . import basics as basics_mod
from . import browser as browser_mod
from . import holo as holo_mod


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    func: Callable[..., Any]

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: dict, func: Callable) -> None:
        self._tools[name] = Tool(name, description, parameters, func)

    def schemas(self) -> list[dict]:
        return [t.schema() for t in self._tools.values()]

    def names(self) -> list[str]:
        return list(self._tools)

    def call(self, name: str, arguments: dict | str) -> str:
        if name not in self._tools:
            return json.dumps({"error": f"ferramenta desconhecida: {name}"})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments else {}
            except json.JSONDecodeError:
                arguments = {}
        try:
            result = self._tools[name].func(**arguments)
        except TypeError as exc:
            return json.dumps({"error": f"argumentos inválidos: {exc}"})
        except Exception as exc:  # noqa: BLE001 - devolve o erro ao modelo
            return json.dumps({"error": str(exc)})
        if isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False)
        return str(result)


def build_default_registry(memory=None, allow_shell: bool = False, actions=None) -> ToolRegistry:
    reg = ToolRegistry()

    reg.register(
        "obter_hora",
        "Devolve a data e hora atuais.",
        {"type": "object", "properties": {}},
        basics_mod.current_time,
    )
    reg.register(
        "obter_meteorologia",
        "Consulta a meteorologia atual e previsão para uma localidade.",
        {
            "type": "object",
            "properties": {
                "local": {"type": "string", "description": "Cidade, ex: 'Lisboa'"}
            },
            "required": ["local"],
        },
        weather_mod.get_weather,
    )
    reg.register(
        "pesquisar_web",
        "Pesquisa na Internet e devolve um resumo dos resultados.",
        {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "O que pesquisar"}
            },
            "required": ["consulta"],
        },
        web_mod.web_search,
    )
    reg.register(
        "listar_ficheiros",
        "Lista ficheiros e pastas dentro da área de trabalho do Jarvis.",
        {
            "type": "object",
            "properties": {
                "caminho": {"type": "string", "description": "Subpasta (opcional)"}
            },
        },
        files_mod.list_dir,
    )
    reg.register(
        "ler_ficheiro",
        "Lê o conteúdo de um ficheiro de texto na área de trabalho.",
        {
            "type": "object",
            "properties": {"caminho": {"type": "string"}},
            "required": ["caminho"],
        },
        files_mod.read_file,
    )
    reg.register(
        "escrever_ficheiro",
        "Cria ou substitui um ficheiro de texto na área de trabalho.",
        {
            "type": "object",
            "properties": {
                "caminho": {"type": "string"},
                "conteudo": {"type": "string"},
            },
            "required": ["caminho", "conteudo"],
        },
        files_mod.write_file,
    )

    if memory is not None:
        reg.register(
            "memorizar",
            "Guarda um facto sobre o utilizador para lembrar no futuro.",
            {
                "type": "object",
                "properties": {
                    "chave": {"type": "string", "description": "Ex: 'nome', 'cidade'"},
                    "valor": {"type": "string"},
                },
                "required": ["chave", "valor"],
            },
            lambda chave, valor: (memory.remember(chave, valor) or f"Memorizado: {chave} = {valor}"),
        )
        reg.register(
            "recordar",
            "Recupera factos guardados sobre o utilizador.",
            {
                "type": "object",
                "properties": {"chave": {"type": "string"}},
            },
            lambda chave=None: memory.recall(chave),
        )

    reg.register(
        "executar_comando",
        "Executa um comando na linha de comandos do sistema. Requer permissão ativa.",
        {
            "type": "object",
            "properties": {"comando": {"type": "string"}},
            "required": ["comando"],
        },
        lambda comando: system_mod.run_command(comando, allow_shell),
    )

    # --- Ferramentas de interface (comandam o HUD) ---
    if actions is not None:

        def _abrir_pagina(alvo: str) -> str:
            info = browser_mod.normalizar_url(alvo)
            actions.add("abrir_pagina", url=info["url"], titulo=info["titulo"])
            return f"A abrir '{info['titulo']}' para o senhor."

        reg.register(
            "abrir_pagina",
            "Abre uma página web para mostrar algo ao utilizador. Aceita um URL "
            "(ex: 'youtube.com') ou um termo de pesquisa (ex: 'notícias de hoje').",
            {
                "type": "object",
                "properties": {
                    "alvo": {"type": "string", "description": "URL ou termo a pesquisar"}
                },
                "required": ["alvo"],
            },
            _abrir_pagina,
        )

        def _construir_modelo(peca: str = "", forma: str = "", cor: str = "") -> str:
            plano = holo_mod.plan_model(peca or None, forma or None, cor or None)
            actions.add("modelo", **plano)
            return f"A projetar '{plano['peca']}' no Holo-Lab (forma: {plano['forma']})."

        reg.register(
            "construir_modelo",
            "Projeta e mostra um modelo 3D holográfico no Holo-Lab (estilo desenho "
            "do fato do filme). Usa para 'constrói', 'mostra em 3D', 'desenha a peça'. "
            "Formas: reator, capacete, manopla, esfera, toroide, cilindro, estrutura.",
            {
                "type": "object",
                "properties": {
                    "peca": {"type": "string", "description": "Peça a construir, ex: 'reator', 'capacete', 'manopla'"},
                    "forma": {"type": "string", "description": "Forma geométrica (opcional)"},
                    "cor": {"type": "string", "description": "Cor em hex, ex: '#35e6ff' (opcional)"},
                },
                "required": ["peca"],
            },
            _construir_modelo,
        )

    return reg
