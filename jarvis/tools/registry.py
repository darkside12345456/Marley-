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
from . import projects as projects_mod
from . import coding as coding_mod
from .. import security as security_mod
from .. import knowledge as knowledge_mod
from .. import mesh as mesh_mod
from ..config import WORKSPACE_DIR
from ..scheduler import get_scheduler
from ..scenes import get_store


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

        def _construir_modelo(peca: str = "", forma: str = "", cor: str = "",
                              tamanho=None, segmentos=None) -> str:
            plano = holo_mod.plan_model(peca or None, forma or None, cor or None,
                                        tamanho, segmentos)
            actions.add("modelo", **plano)
            return f"A projetar '{plano['peca']}' no Holo-Lab (forma: {plano['forma']})."

        reg.register(
            "construir_modelo",
            "Projeta e mostra um modelo 3D holográfico no Holo-Lab (estilo desenho "
            "do fato do filme). Usa para 'constrói', 'mostra em 3D', 'desenha a peça'. "
            "Formas: reator, capacete, manopla, esfera, toroide, cilindro, estrutura. "
            "'tamanho' escala a peça (0.2 a 3) e 'segmentos' aumenta o detalhe.",
            {
                "type": "object",
                "properties": {
                    "peca": {"type": "string", "description": "Peça a construir, ex: 'reator', 'capacete'"},
                    "forma": {"type": "string", "description": "Forma geométrica (opcional)"},
                    "cor": {"type": "string", "description": "Cor em hex, ex: '#35e6ff' (opcional)"},
                    "tamanho": {"type": "number", "description": "Escala 0.2–3 (opcional)"},
                    "segmentos": {"type": "number", "description": "Detalhe 6–48 (opcional)"},
                },
                "required": ["peca"],
            },
            _construir_modelo,
        )

        def _construir_cena(partes) -> str:
            plano = holo_mod.plan_scene(partes)
            if "erro" in plano:
                return plano["erro"]
            actions.add("cena", partes=plano["partes"])
            return f"A montar uma cena com {len(plano['partes'])} peça(s) no Holo-Lab."

        reg.register(
            "construir_cena",
            "Monta uma cena 3D composta por várias peças posicionadas (ex: montar "
            "um robô ou uma estrutura a partir de vários blocos). Cada parte tem "
            "'forma' e opcionalmente 'cor', 'tamanho' e 'pos' [x,y,z].",
            {
                "type": "object",
                "properties": {
                    "partes": {
                        "type": "array",
                        "description": "Lista de peças, cada uma {forma, cor?, tamanho?, pos?}",
                        "items": {"type": "object"},
                    }
                },
                "required": ["partes"],
            },
            _construir_cena,
        )

    # --- Cibersegurança (defensivo, só de leitura) ---
    def _painel(titulo: str, texto: str) -> None:
        if actions is not None:
            actions.add("painel", titulo=titulo, texto=texto)

    def _verificar_ameacas() -> dict:
        rel = security_mod.verificar_ameacas()
        _painel(f"🛡️ Segurança — risco {rel['nivel']}", rel["relatorio"])
        return rel

    reg.register(
        "verificar_ameacas",
        "Faz uma verificação de segurança ao computador (processos, rede e itens de "
        "arranque) e devolve um relatório de risco. Só de leitura — nunca apaga nada.",
        {"type": "object", "properties": {}},
        _verificar_ameacas,
    )
    reg.register(
        "analisar_processos",
        "Lista processos em execução e assinala indícios suspeitos.",
        {"type": "object", "properties": {}},
        security_mod.analisar_processos,
    )
    reg.register(
        "analisar_rede",
        "Lista portas à escuta e ligações de rede ativas, assinalando as de risco.",
        {"type": "object", "properties": {}},
        security_mod.analisar_rede,
    )
    reg.register(
        "analisar_ficheiros",
        "Procura ficheiros com características de risco numa pasta (só de leitura).",
        {
            "type": "object",
            "properties": {"caminho": {"type": "string", "description": "Pasta a analisar"}},
            "required": ["caminho"],
        },
        security_mod.analisar_ficheiros,
    )
    reg.register(
        "calcular_hash",
        "Calcula o SHA-256 de um ficheiro (para verificação manual, ex: VirusTotal).",
        {
            "type": "object",
            "properties": {"caminho": {"type": "string"}},
            "required": ["caminho"],
        },
        security_mod.calcular_hash,
    )

    # --- Criação de aplicações (isolada na sandbox 'workspace/') ---
    def _criar_projeto(nome: str, tipo: str = "web", descricao: str = "") -> dict:
        resultado = projects_mod.criar_projeto(nome, tipo, descricao)
        if resultado.get("ok"):
            _painel(
                f"🧩 App criada: {nome}",
                f"Tipo: {resultado['tipo']}\nPasta: workspace/{resultado['pasta']}\n"
                f"Ficheiros: {', '.join(resultado['ficheiros'])}",
            )
            if actions is not None and resultado.get("abrir_url"):
                actions.add("abrir_pagina", url=resultado["abrir_url"], titulo=f"App: {nome}")
        return resultado

    reg.register(
        "criar_projeto",
        "Cria uma aplicação/projeto a partir de um modelo, dentro da área de "
        "trabalho segura. Tipos: web, react, python, flask, node, api (Flask+SQLite). "
        "As apps 'web' e 'react' abrem automaticamente no browser.",
        {
            "type": "object",
            "properties": {
                "nome": {"type": "string"},
                "tipo": {"type": "string", "description": "web, react, python, flask, node ou api"},
                "descricao": {"type": "string"},
            },
            "required": ["nome"],
        },
        _criar_projeto,
    )

    # --- Exportar peça 3D para .obj (impressão 3D / software 3D) ---
    def _exportar_modelo(peca: str = "", forma: str = "", tamanho=None,
                         segmentos=None, nome: str = "") -> dict:
        plano = holo_mod.plan_model(peca or None, forma or None, None, tamanho, segmentos)
        base = (nome or plano["forma"]).strip().replace("/", "-") or "peca"
        destino = WORKSPACE_DIR / f"{base}.obj"
        mesh_mod.exportar_obj(plano["forma"], destino, plano["escala"], plano["segmentos"])
        rel = destino.relative_to(WORKSPACE_DIR)
        _painel("💾 Modelo exportado",
                f"Peça: {plano['forma']}\nFicheiro: workspace/{rel}\n"
                f"Abre num software 3D ou fatiador de impressão 3D.")
        return {"ok": True, "ficheiro": f"workspace/{rel}", "forma": plano["forma"]}

    reg.register(
        "exportar_modelo",
        "Exporta uma peça do Holo-Lab para um ficheiro .obj (formato 3D aberto, "
        "para software 3D ou impressão 3D). Guarda na área de trabalho.",
        {
            "type": "object",
            "properties": {
                "peca": {"type": "string", "description": "Peça, ex: 'reator', 'capacete'"},
                "forma": {"type": "string"},
                "tamanho": {"type": "number"},
                "segmentos": {"type": "number", "description": "Detalhe (opcional)"},
                "nome": {"type": "string", "description": "Nome do ficheiro (opcional)"},
            },
            "required": ["peca"],
        },
        _exportar_modelo,
    )

    # --- Agendar verificações de segurança automáticas ---
    def _agendar_verificacao(horas: float = 24) -> dict:
        estado = get_scheduler().iniciar(float(horas))
        if estado["ativo"]:
            _painel("⏰ Verificação de segurança agendada",
                    f"O Jarvis vai verificar ameaças a cada {estado['intervalo_horas']:g} h.")
        else:
            _painel("⏰ Agendamento desligado", "As verificações automáticas foram paradas.")
        return estado

    reg.register(
        "agendar_verificacao",
        "Agenda verificações de segurança automáticas de X em X horas (0 desliga).",
        {
            "type": "object",
            "properties": {"horas": {"type": "number", "description": "Intervalo em horas (0 = desligar)"}},
            "required": ["horas"],
        },
        _agendar_verificacao,
    )
    reg.register(
        "estado_seguranca",
        "Mostra o estado do agendamento e o resultado da última verificação automática.",
        {"type": "object", "properties": {}},
        lambda: get_scheduler().estado(),
    )

    # --- Guardar / carregar projetos 3D do Holo-Lab ---
    def _guardar_projeto(nome: str) -> dict:
        res = get_store().guardar(nome)
        if res.get("ok"):
            _painel("💾 Projeto 3D guardado", f"'{nome}' com {res['pecas']} peça(s).")
        return res

    def _carregar_projeto(nome: str) -> dict:
        res = get_store().carregar(nome)
        if res.get("ok"):
            if actions is not None:
                actions.add("cena", partes=res["partes"])
            _painel("📂 Projeto 3D carregado", f"'{res['nome']}' com {len(res['partes'])} peça(s).")
        return res

    reg.register(
        "guardar_projeto",
        "Guarda a cena atual do Holo-Lab como um projeto 3D com um nome, para "
        "recuperar noutra sessão.",
        {"type": "object", "properties": {"nome": {"type": "string"}}, "required": ["nome"]},
        _guardar_projeto,
    )
    reg.register(
        "carregar_projeto",
        "Carrega um projeto 3D guardado e mostra-o no Holo-Lab.",
        {"type": "object", "properties": {"nome": {"type": "string"}}, "required": ["nome"]},
        _carregar_projeto,
    )
    reg.register(
        "listar_projetos",
        "Lista os projetos 3D guardados.",
        {"type": "object", "properties": {}},
        lambda: {"projetos": get_store().listar()},
    )
    reg.register(
        "apagar_projeto",
        "Apaga um projeto 3D guardado.",
        {"type": "object", "properties": {"nome": {"type": "string"}}, "required": ["nome"]},
        lambda nome: get_store().apagar(nome),
    )
    reg.register(
        "renomear_projeto",
        "Renomeia um projeto 3D guardado.",
        {"type": "object", "properties": {"nome": {"type": "string"}, "novo": {"type": "string"}},
         "required": ["nome", "novo"]},
        lambda nome, novo: get_store().renomear(nome, novo),
    )

    # --- Programação em qualquer linguagem ---
    def _escrever_codigo(nome: str, linguagem: str, codigo: str) -> dict:
        res = coding_mod.guardar_codigo(nome, linguagem, codigo)
        if res.get("ok"):
            _painel(f"💻 Código escrito ({res['linguagem']})",
                    f"Ficheiro: {res['ficheiro']} · {res['linhas']} linha(s).")
            if actions is not None and res["ficheiro"].endswith((".html", ".htm")):
                rel = res["ficheiro"].split("workspace/", 1)[-1]
                actions.add("abrir_pagina", url=f"/workspace/{rel}", titulo=nome)
        return res

    reg.register(
        "escrever_codigo",
        "Escreve código em QUALQUER linguagem (Python, JS, C++, Rust, Go, Java, "
        "SQL, etc.) e guarda o ficheiro na área de trabalho. Tu geras o código; "
        "esta ferramenta apenas o grava com a extensão certa.",
        {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do ficheiro (sem extensão é ok)"},
                "linguagem": {"type": "string", "description": "Ex: 'python', 'rust', 'c++'"},
                "codigo": {"type": "string", "description": "O código completo"},
            },
            "required": ["nome", "linguagem", "codigo"],
        },
        _escrever_codigo,
    )

    # --- Conhecimento de cibersegurança (defensivo) ---
    def _consultar_seguranca(topico: str = "") -> dict:
        res = knowledge_mod.consultar(topico)
        if res.get("conselho"):
            _painel(f"🔐 Segurança: {res['topico']}", res["conselho"])
        return res

    reg.register(
        "consultar_seguranca",
        "Consulta conhecimento de cibersegurança defensiva sobre um tópico "
        "(palavras-passe, phishing, ransomware, 2FA, OWASP, backups, etc.).",
        {"type": "object", "properties": {"topico": {"type": "string"}}},
        _consultar_seguranca,
    )
    reg.register(
        "listar_topicos_seguranca",
        "Lista os tópicos de cibersegurança disponíveis.",
        {"type": "object", "properties": {}},
        lambda: {"topicos": knowledge_mod.listar_topicos()},
    )

    return reg
