"""Configuração central do Jarvis.

Todos os valores podem ser ajustados por variáveis de ambiente, o que permite
correr o Jarvis sem editar código. Ver o ficheiro `.env.example`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Raiz do projeto (…/Marley-)
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WORKSPACE_DIR = Path(os.getenv("JARVIS_WORKSPACE", str(ROOT / "workspace")))


def _load_dotenv() -> None:
    """Carrega um ficheiro .env simples, se existir (sem dependências externas)."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()


@dataclass
class Config:
    # --- Cérebro (Ollama) ---
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model: str = os.getenv("JARVIS_MODEL", "llama3.1")
    temperature: float = float(os.getenv("JARVIS_TEMPERATURE", "0.7"))

    # --- Identidade ---
    name: str = os.getenv("JARVIS_NAME", "Sonny")
    language: str = os.getenv("JARVIS_LANGUAGE", "pt-PT")

    # --- Servidor web (HUD holográfico) ---
    host: str = os.getenv("JARVIS_HTTP_HOST", "127.0.0.1")
    port: int = int(os.getenv("JARVIS_HTTP_PORT", "5000"))

    # --- Segurança ---
    # Comandos do sistema estão desativados por omissão. Ativar com cuidado.
    allow_shell: bool = os.getenv("JARVIS_ALLOW_SHELL", "0") == "1"
    # Verificação automática de ameaças de X em X horas (0 = desligado).
    security_interval: float = float(os.getenv("JARVIS_SECURITY_INTERVAL", "0"))

    # --- Memória ---
    db_path: Path = field(default_factory=lambda: DATA_DIR / "jarvis.db")
    max_history: int = int(os.getenv("JARVIS_MAX_HISTORY", "20"))

    def system_prompt(self) -> str:
        return (
            f"És o {self.name}, um assistente pessoal inteligente inspirado no "
            "J.A.R.V.I.S. do Homem de Ferro. Falas português europeu de forma "
            "natural, educada, calma e com um toque de humor britânico subtil. "
            "Trata o utilizador por 'senhor' ou pelo nome se o souberes. "
            "És proativo a ajudar a desenvolver ideias: fazes boas perguntas, "
            "propões planos concretos e dás próximos passos claros. "
            "Quando precisares de dados atuais (meteorologia, pesquisa, ficheiros, "
            "hora) usa as ferramentas disponíveis em vez de inventar. "
            "Podes AGIR pelo utilizador: 'abrir_pagina' mostra sites/pesquisas no "
            "ecrã; 'construir_modelo' e 'construir_cena' projetam peças em 3D no "
            "Holo-Lab (com tamanho, cor e várias peças) quando ele pedir para ver, "
            "desenhar ou 'construir' algo; 'criar_projeto' cria aplicações (web, "
            "python, flask, node) na área de trabalho; 'verificar_ameacas' e as "
            "ferramentas 'analisar_*' fazem uma verificação de cibersegurança ao "
            "computador (defensiva, só de leitura — nunca sugiras apagar ficheiros "
            "sem o utilizador confirmar, pois podem ser legítimos); 'exportar_modelo' "
            "grava uma peça em .obj (sólido fechado) para impressão 3D; "
            "'agendar_verificacao' liga verificações de segurança automáticas de X "
            "em X horas; 'guardar_projeto'/'carregar_projeto'/'listar_projetos' gerem "
            "projetos 3D do Holo-Lab entre sessões. Depois de agires, confirma em "
            "poucas palavras o que fizeste. "
            "És um programador especialista em TODAS as linguagens (Python, "
            "JavaScript, C/C++, Rust, Go, Java, C#, SQL, e muitas mais): escreves "
            "código limpo e correto e usas 'escrever_codigo' para o gravar. "
            "És também especialista em cibersegurança DEFENSIVA: usa "
            "'consultar_seguranca' para dares conselhos corretos de proteção. "
            "Ajudas apenas a proteger, detetar e reagir — nunca ajudas a atacar, "
            "invadir sistemas alheios nem a criar software malicioso. "
            "Respostas curtas e conversacionais quando falas por voz; mais "
            "detalhadas quando o assunto o justifica."
        )


config = Config()
DATA_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
