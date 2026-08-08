"""Verificador de ameaças — DEFENSIVO e SÓ DE LEITURA.

Princípios de cibersegurança aplicados:
  * Só leitura: nunca apaga, move ou altera nada. Apenas deteta e aconselha.
  * Privacidade: não envia dados para lado nenhum. Os hashes são mostrados
    para o utilizador verificar (ex: VirusTotal), nada é carregado.
  * Conservador: os alertas são "indícios", não prova. Evita falsos alarmes.
  * Robusto: tolera falta de permissões e ambientes diferentes sem rebentar.

Usa o `psutil` se estiver instalado (recomendado); caso contrário degrada com
alternativas da biblioteca padrão. Instalar: pip install -r requirements-seg.txt
"""
from __future__ import annotations

import hashlib
import os
import platform
from pathlib import Path

try:
    import psutil  # type: ignore
    _HAS_PSUTIL = True
except Exception:  # pragma: no cover
    _HAS_PSUTIL = False

SISTEMA = platform.system()  # 'Linux', 'Windows', 'Darwin'

# Diretórios onde processos/ficheiros executáveis são suspeitos.
_DIRS_SUSPEITOS = ["/tmp", "/var/tmp", "/dev/shm"]
# Palavras associadas a malware comum (miners, backdoors). Lista curta e conservadora.
_NOMES_SUSPEITOS = ["xmrig", "minerd", "cryptonight", "kdevtmpfsi", "kinsing",
                    "ncat", "netcat", "meterpreter", "mimikatz"]
# Portas frequentemente associadas a acesso remoto/backdoors (informativo).
_PORTAS_ATENCAO = {23, 2323, 4444, 5555, 6667, 31337, 12345, 1080, 9001}


def _dir_suspeito(caminho: str | None) -> bool:
    if not caminho:
        return False
    c = caminho.lower()
    return any(c.startswith(d) for d in _DIRS_SUSPEITOS)


# ---------------------------------------------------------------- processos
def analisar_processos(limite: int = 400) -> dict:
    """Lista processos e assinala indícios suspeitos (sem os terminar)."""
    suspeitos: list[dict] = []
    total = 0

    if _HAS_PSUTIL:
        for proc in psutil.process_iter(["pid", "name", "exe", "username"]):
            total += 1
            if total > limite:
                break
            try:
                info = proc.info
                nome = (info.get("name") or "").lower()
                exe = info.get("exe") or ""
            except Exception:
                continue
            motivos = []
            if _dir_suspeito(exe):
                motivos.append(f"executável numa pasta temporária ({exe})")
            if any(k in nome for k in _NOMES_SUSPEITOS):
                motivos.append("nome associado a software malicioso conhecido")
            if motivos:
                suspeitos.append({"pid": info.get("pid"), "nome": info.get("name"),
                                  "caminho": exe, "indicios": motivos})
    elif SISTEMA == "Linux":
        proc_root = Path("/proc")
        for pdir in proc_root.iterdir():
            if not pdir.name.isdigit():
                continue
            total += 1
            if total > limite:
                break
            try:
                nome = (pdir / "comm").read_text().strip().lower()
            except Exception:
                nome = ""
            try:
                exe = os.readlink(pdir / "exe")
            except Exception:
                exe = ""
            motivos = []
            if _dir_suspeito(exe):
                motivos.append(f"executável numa pasta temporária ({exe})")
            if any(k in nome for k in _NOMES_SUSPEITOS):
                motivos.append("nome associado a software malicioso conhecido")
            if motivos:
                suspeitos.append({"pid": int(pdir.name), "nome": nome,
                                  "caminho": exe, "indicios": motivos})
    else:
        return {"suportado": False,
                "nota": "Instala o psutil para analisar processos neste sistema."}

    return {"total_analisados": total, "suspeitos": suspeitos}


# -------------------------------------------------------------------- rede
def analisar_rede() -> dict:
    """Lista portas à escuta e ligações estabelecidas; assinala portas de risco."""
    if not _HAS_PSUTIL:
        return {"suportado": False,
                "nota": "Instala o psutil para analisar a rede (requirements-seg.txt)."}
    escuta: list[dict] = []
    ligacoes: list[dict] = []
    alertas: list[str] = []
    try:
        conns = psutil.net_connections(kind="inet")
    except Exception as exc:
        return {"suportado": False, "nota": f"Sem permissão para ler a rede: {exc}"}

    for c in conns:
        try:
            lport = c.laddr.port if c.laddr else None
            if c.status == "LISTEN":
                escuta.append({"porta": lport, "endereco": c.laddr.ip if c.laddr else ""})
                if lport in _PORTAS_ATENCAO:
                    alertas.append(f"porta {lport} à escuta (frequentemente usada por acesso remoto)")
            elif c.status == "ESTABLISHED" and c.raddr:
                rport = c.raddr.port
                ligacoes.append({"remoto": f"{c.raddr.ip}:{rport}"})
                if rport in _PORTAS_ATENCAO:
                    alertas.append(f"ligação ativa para {c.raddr.ip}:{rport} (porta de atenção)")
        except Exception:
            continue

    return {
        "portas_a_escuta": escuta[:50],
        "ligacoes_ativas": len(ligacoes),
        "alertas": sorted(set(alertas)),
    }


# --------------------------------------------------------------- ficheiros
def _sha256(caminho: Path, limite_mb: int = 100) -> str | None:
    try:
        if caminho.stat().st_size > limite_mb * 1024 * 1024:
            return None
        h = hashlib.sha256()
        with caminho.open("rb") as f:
            for bloco in iter(lambda: f.read(65536), b""):
                h.update(bloco)
        return h.hexdigest()
    except Exception:
        return None


def analisar_ficheiros(caminho: str, max_ficheiros: int = 500) -> dict:
    """Procura ficheiros com características de risco numa pasta (não recursivo
    fundo; ignora ligações simbólicas por segurança)."""
    base = Path(caminho).expanduser()
    if not base.exists():
        return {"erro": f"caminho inexistente: {caminho}"}
    suspeitos: list[dict] = []
    contados = 0

    for root, dirs, files in os.walk(base, followlinks=False):
        for nome in files:
            contados += 1
            if contados > max_ficheiros:
                break
            p = Path(root) / nome
            if p.is_symlink():
                continue
            motivos = []
            baixo = nome.lower()
            # dupla extensão a tentar disfarçar um executável
            if any(baixo.endswith(e) for e in (".pdf.exe", ".doc.exe", ".jpg.exe",
                                               ".txt.exe", ".pdf.scr")):
                motivos.append("dupla extensão (disfarça um executável)")
            # executável numa pasta temporária
            if baixo.endswith((".exe", ".scr", ".bat", ".cmd", ".js", ".vbs", ".ps1")) \
                    and _dir_suspeito(str(p)):
                motivos.append("script/executável numa pasta temporária")
            # bit de execução no Linux fora de pastas normais
            try:
                if SISTEMA != "Windows" and os.access(p, os.X_OK) and _dir_suspeito(str(p)):
                    motivos.append("ficheiro executável numa pasta temporária")
            except Exception:
                pass
            if motivos:
                suspeitos.append({"ficheiro": str(p), "indicios": motivos,
                                  "sha256": _sha256(p)})
        if contados > max_ficheiros:
            break

    return {"analisados": contados, "suspeitos": suspeitos,
            "nota": "Verifica os hashes SHA-256 em virustotal.com se tiveres dúvidas."}


def calcular_hash(caminho: str) -> dict:
    """SHA-256 de um ficheiro (para verificação manual em VirusTotal, etc.)."""
    p = Path(caminho).expanduser()
    if not p.is_file():
        return {"erro": "ficheiro inexistente"}
    return {"ficheiro": str(p), "sha256": _sha256(p, limite_mb=500)}


# ----------------------------------------------------------- verificação geral
def _dirs_arranque() -> list[str]:
    casa = Path.home()
    candidatos = []
    if SISTEMA == "Linux":
        candidatos += [casa / ".config/autostart", casa / ".config/systemd/user"]
    elif SISTEMA == "Darwin":
        candidatos += [casa / "Library/LaunchAgents"]
    return [str(c) for c in candidatos if c.exists()]


def analisar_arranque() -> dict:
    """Lista itens configurados para arrancar com o sistema (só leitura)."""
    itens: list[dict] = []
    for d in _dirs_arranque():
        try:
            for f in Path(d).iterdir():
                itens.append({"local": d, "item": f.name})
        except Exception:
            continue
    if SISTEMA == "Windows":
        try:
            import winreg  # type: ignore
            chave = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run")
            i = 0
            while True:
                try:
                    nome, valor, _ = winreg.EnumValue(chave, i)
                    itens.append({"local": "HKCU\\...\\Run", "item": nome, "valor": valor})
                    i += 1
                except OSError:
                    break
        except Exception:
            pass
    return {"itens_de_arranque": itens}


def verificar_ameacas() -> dict:
    """Verificação rápida e global. Devolve um relatório legível + dados."""
    procs = analisar_processos()
    rede = analisar_rede()
    arranque = analisar_arranque()

    n_proc = len(procs.get("suspeitos", []))
    n_rede = len(rede.get("alertas", []))

    if n_proc:
        nivel = "ALTO"
    elif n_rede:
        nivel = "MÉDIO"
    else:
        nivel = "BAIXO"

    linhas = [f"Nível de risco: {nivel}",
              f"Processos suspeitos: {n_proc}",
              f"Alertas de rede: {n_rede}"]
    for s in procs.get("suspeitos", [])[:5]:
        linhas.append(f"  • processo '{s['nome']}' (PID {s['pid']}): {', '.join(s['indicios'])}")
    for a in rede.get("alertas", [])[:5]:
        linhas.append(f"  • rede: {a}")
    if nivel == "BAIXO":
        linhas.append("Sem indícios óbvios de ameaça. (Isto não substitui um antivírus.)")
    else:
        linhas.append("Recomenda-se investigar os itens acima antes de agir. "
                      "Não apagues nada sem confirmar — pode ser legítimo.")

    return {
        "nivel": nivel,
        "relatorio": "\n".join(linhas),
        "processos": procs,
        "rede": rede,
        "arranque": arranque,
        "sistema": SISTEMA,
        "psutil_disponivel": _HAS_PSUTIL,
        "aviso": "Verificação de leitura, indicativa. Não substitui um antivírus dedicado.",
    }
