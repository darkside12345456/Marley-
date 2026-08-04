"""Jarvis — assistente pessoal inteligente estilo J.A.R.V.I.S."""
from .assistant import Assistant
from .config import Config, config

__version__ = "0.1.0"
__all__ = ["Assistant", "Config", "config", "__version__"]
