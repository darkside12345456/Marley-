"""Ferramentas do Jarvis.

Cada ferramenta é uma função Python registada com um esquema JSON compatível
com a API de "tools" do Ollama. O `Assistant` executa-as num ciclo quando o
modelo as pede.
"""
from .registry import ToolRegistry, build_default_registry

__all__ = ["ToolRegistry", "build_default_registry"]
