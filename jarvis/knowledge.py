"""Base de conhecimento de cibersegurança — DEFENSIVA e educativa.

Conselhos corretos e concisos sobre proteção e boas práticas. Estritamente
defensivo: proteger, detetar, reagir. Não contém técnicas de ataque.
"""
from __future__ import annotations

SEGURANCA: dict[str, str] = {
    "palavras-passe": (
        "Usa palavras-passe longas (12+ caracteres) e únicas por serviço. "
        "Prefere frases-passe. Nunca reutilizes a mesma. Usa um gestor de "
        "palavras-passe para as guardar em segurança."),
    "autenticacao de dois fatores": (
        "Ativa a autenticação de dois fatores (2FA/MFA) em todas as contas "
        "importantes. Prefere apps de autenticação (TOTP) ou chaves físicas "
        "(FIDO2) em vez de SMS, que é menos seguro."),
    "phishing": (
        "Desconfia de mensagens que criam urgência, pedem dados ou têm links "
        "estranhos. Verifica o remetente e o endereço real dos links (passa o "
        "rato por cima). Nunca introduzas credenciais a partir de um link de "
        "email; vai ao site diretamente."),
    "malware": (
        "Instala software só de fontes oficiais. Mantém um antivírus ativo e "
        "atualizado. Não abras anexos inesperados. Cuidado com ficheiros de "
        "dupla extensão (ex: fatura.pdf.exe)."),
    "ransomware": (
        "A melhor defesa são backups offline/desligados e testados. Mantém "
        "tudo atualizado, desativa macros do Office por omissão e limita "
        "privilégios de administrador. Se fores atingido, isola a máquina da "
        "rede e não pagues sem aconselhamento."),
    "firewall": (
        "Mantém a firewall do sistema ligada. Bloqueia tudo o que não precisas "
        "e só abre as portas estritamente necessárias. Revê regras antigas."),
    "vpn": (
        "Uma VPN cifra o teu tráfego e é útil em redes Wi-Fi públicas. Escolhe "
        "um fornecedor de confiança com política de não registo (no-logs)."),
    "wi-fi": (
        "Usa WPA3 (ou WPA2) com palavra-passe forte. Muda as credenciais por "
        "omissão do router, atualiza o firmware e desativa o WPS."),
    "backups": (
        "Segue a regra 3-2-1: 3 cópias, em 2 tipos de suporte, 1 fora do local. "
        "Testa restauros regularmente. Mantém pelo menos uma cópia offline."),
    "atualizacoes": (
        "Ativa atualizações automáticas do sistema e das apps. A maioria dos "
        "ataques explora falhas já corrigidas por patches."),
    "engenharia social": (
        "Atacantes manipulam pessoas, não só máquinas. Confirma pedidos "
        "sensíveis por um segundo canal, desconfia de pressão e nunca partilhes "
        "códigos de verificação com ninguém."),
    "owasp": (
        "O OWASP Top 10 lista os riscos web mais comuns: quebras de controlo de "
        "acesso, falhas criptográficas, injeção, design inseguro, más "
        "configurações, componentes vulneráveis, falhas de autenticação, "
        "integridade de software/dados, falhas de registo e SSRF."),
    "injecao sql": (
        "Previne injeção SQL com consultas parametrizadas (prepared statements) "
        "e ORMs. Nunca construas SQL concatenando input do utilizador. Valida e "
        "limita as permissões da conta de base de dados."),
    "xss": (
        "Contra XSS: escapa/encoda a saída no contexto certo (HTML, atributo, "
        "JS), valida input, e usa uma Content-Security-Policy. Marca cookies "
        "como HttpOnly."),
    "criptografia": (
        "Cifra dados sensíveis em repouso e em trânsito (TLS). Usa algoritmos "
        "modernos (AES-256, ChaCha20) e nunca inventes o teu próprio esquema "
        "criptográfico. Guarda as chaves em segurança."),
    "gestor de palavras-passe": (
        "Um gestor (ex: Bitwarden, KeePass, 1Password) gera e guarda palavras-"
        "passe únicas e fortes, protegidas por uma palavra-passe mestra e 2FA."),
    "privacidade": (
        "Partilha o mínimo de dados. Revê permissões de apps, usa contas "
        "separadas quando fizer sentido, e conhece os teus direitos (ex: RGPD "
        "na UE: acesso, retificação e apagamento dos teus dados)."),
    "resposta a incidentes": (
        "Plano básico: preparar, detetar, conter, erradicar, recuperar e rever. "
        "Isola a máquina afetada, preserva registos, muda credenciais e aprende "
        "com o incidente para reforçar defesas."),
    "navegacao segura": (
        "Verifica o HTTPS e o domínio correto, mantém o browser atualizado, usa "
        "um bloqueador fiável e evita descarregar software de sites duvidosos."),
}


def listar_topicos() -> list[str]:
    return sorted(SEGURANCA)


def consultar(topico: str) -> dict:
    t = (topico or "").lower().strip()
    if not t:
        return {"topicos": listar_topicos()}
    # correspondência direta ou por subcadeia
    for chave, conselho in SEGURANCA.items():
        if t == chave:
            return {"topico": chave, "conselho": conselho}
    for chave, conselho in SEGURANCA.items():
        if t in chave or chave in t or any(p in chave for p in t.split()):
            return {"topico": chave, "conselho": conselho}
    return {"topico": topico, "conselho": None, "sugestoes": listar_topicos()}
