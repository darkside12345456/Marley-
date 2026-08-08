# 🤖 J.A.R.V.I.S.

Um assistente pessoal inteligente inspirado no J.A.R.V.I.S. do Homem de Ferro.
Fala e ouve, tem memória, usa ferramentas (meteorologia, pesquisa, ficheiros,
comandos do sistema) e ajuda-te a **desenvolver ideias** — tudo com um **HUD
holográfico** ao estilo do filme e a correr **localmente e gratuito** com o
[Ollama](https://ollama.com).

> Nota honesta: hologramas físicos reais não são possíveis por software. O que
> tens aqui é uma interface visual futurista "holográfica" (orbe/reator animado
> que reage quando ouve, pensa e fala) muito ao estilo Jarvis.

---

## ✨ O que faz

- **Voz** — fala e ouve. No HUD web usa a voz do próprio browser (sem instalar
  nada). No terminal há um modo de voz opcional em Python. Tem **palavra de
  ativação**: liga o 🎧 e diz *"Jarvis…"* para ativar sem clicar.
- **Cérebro local** — usa o Ollama, sem chaves de API nem custos por uso.
- **Memória** — lembra-se da conversa e de factos sobre ti (SQLite).
- **Ferramentas** — meteorologia, pesquisa na web, ler/escrever ficheiros,
  hora, e comandos do sistema (desligados por segurança até tu permitires).
- **Age por ti** — abre páginas e pesquisas no ecrã quando pedires.
- **Holo-Lab 3D paramétrico** — "constrói" o que pedires em wireframe holográfico
  (peças com tamanho/cor à escolha e cenas com várias peças), estilo desenho do
  fato no filme.
- **Cria aplicações** — gera projetos (web, python, flask, node) na sandbox e
  abre as apps web no browser.
- **Cibersegurança** — verifica ameaças no PC (processos, rede, arranque). É
  **defensivo e só de leitura**: deteta e avisa, nunca apaga nada.
- **HUD holográfico** — orbe/reator animado, ondas de voz e transcrição.

---

## 🚀 Começar

### 1. Instalar o Ollama (o "cérebro")

Descarrega em **https://ollama.com**, depois puxa um modelo com suporte a
ferramentas:

```bash
ollama pull llama3.1      # recomendado (bom com ferramentas)
ollama serve              # normalmente já corre em segundo plano
```

### 2. Instalar as dependências do Jarvis

```bash
pip install -r requirements.txt
```

### 3. (Opcional) Configurar

```bash
cp .env.example .env      # e ajusta o modelo, porta, etc. se quiseres
```

### 4. Arrancar

```bash
python -m jarvis          # abre o HUD holográfico no browser  (recomendado)
```

Abre automaticamente `http://127.0.0.1:5000`. Carrega no 🎙️ e fala, ou escreve.

---

## 🖥️ Modos de utilização

| Comando | O que faz |
|---|---|
| `python -m jarvis` | HUD holográfico no browser (voz + visual) |
| `python -m jarvis voz` | Conversa por voz no terminal |
| `python -m jarvis texto` | Conversa por texto no terminal |
| `python -m jarvis "que horas são?"` | Pergunta única e sai |

### Voz no terminal (opcional)

O HUD web já fala e ouve pelo browser. Se quiseres voz no **terminal**:

```bash
pip install -r requirements-voz.txt
python -m jarvis voz
```

---

## 🔧 Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `obter_hora` | Data e hora atuais |
| `obter_meteorologia` | Meteorologia (via Open-Meteo, grátis) |
| `pesquisar_web` | Pesquisa na Internet (via DuckDuckGo) |
| `listar_ficheiros` / `ler_ficheiro` / `escrever_ficheiro` | Ficheiros na pasta `workspace/` |
| `memorizar` / `recordar` | Guarda e recupera factos sobre ti |
| `abrir_pagina` | Abre um site ou pesquisa no ecrã |
| `construir_modelo` / `construir_cena` | Projeta peças 3D no Holo-Lab (com tamanho/cor/composição) |
| `criar_projeto` | Cria uma aplicação (web, react, python, flask, node, api) na sandbox |
| `exportar_modelo` | Exporta uma peça 3D (sólido fechado) para `.obj` |
| `guardar_projeto` / `carregar_projeto` / `listar_projetos` | Gere projetos 3D entre sessões |
| `verificar_ameacas` / `analisar_processos` / `analisar_rede` / `analisar_ficheiros` / `calcular_hash` | Cibersegurança (só de leitura) |
| `agendar_verificacao` / `estado_seguranca` | Verificações de segurança automáticas |
| `executar_comando` | Comandos do sistema — **desligado por omissão** |

### 🔬 Holo-Lab (peças 3D estilo filme)

Pede ao Jarvis, por voz ou texto, coisas como:

> "Constrói-me o reator" · "Mostra-me o capacete em 3D" · "Desenha uma manopla"

Ele projeta a peça num **wireframe holográfico a rodar**. Também tens um botão
🔬 no HUD para abrir o Holo-Lab e trocar de peça manualmente (reator, capacete,
manopla, núcleo, anel, motor, estrutura).

**Controlos:** arrasta com o rato para **rodar** e usa a **roda do rato para
zoom** (funciona também por toque no telemóvel).

**Editor visual:** carrega em **✏️ Editor**, escolhe uma peça e usa **＋** para a
adicionar; depois **arrasta as peças com o rato** para as posicionar e monta
cenas (ex: um robô). **🗑** remove a peça selecionada.

**Guardar/carregar projetos:** **💾** guarda a cena com um nome e **📂** carrega-a
noutra sessão. Também por voz: *"guarda o projeto como reator-v2"*,
*"carrega o projeto reator-v2"*.

**Exportar para impressão 3D:** botão **⬇ .obj** ou *"exporta o reator para .obj"*.
Todas as peças são geradas como **sólidos fechados (watertight)** — malhas
manifold prontas a fatiar e imprimir.

> Nota: isto é **visualização e modelação 3D**, não fabrico físico — o software
> desenha, mostra e exporta o modelo; a impressão é feita pela tua impressora 3D
> a partir do ficheiro `.obj`.

### 🧩 Criar aplicações

> "Cria-me uma app web chamada Agenda" · "Faz um projeto flask chamado api"

O Jarvis gera a estrutura do projeto dentro de `workspace/` (isolado do resto do
PC). Tipos: **web, react, python, flask, node, api** (Flask + SQLite com CRUD).
As apps **web** e **react** abrem logo no browser.

### 🛡️ Cibersegurança (verificar ameaças)

> "Verifica se há ameaças no meu PC" · botão **🛡️** no HUD

Faz uma verificação **defensiva e só de leitura** e mostra um relatório de risco
(processos, rede e itens de arranque). Princípios:

- **Nunca apaga nem altera nada** — só deteta e aconselha (evita estragos por
  falsos positivos).
- **Privacidade** — não envia dados para lado nenhum. Os hashes SHA-256 são
  mostrados para tu verificares (ex: em [virustotal.com](https://virustotal.com)).
- **Indicativo** — não substitui um antivírus dedicado.

Para análise completa de processos e rede, instala o `psutil` (opcional):

```bash
pip install -r requirements-seg.txt
```

**Verificações automáticas:** pede *"verifica a segurança a cada 6 horas"* (ou
usa `JARVIS_SECURITY_INTERVAL` no `.env`). O Jarvis passa a verificar em segundo
plano, guarda um registo em `data/security_log.jsonl` e **avisa-te no HUD** (por
voz e num painel) se o risco subir.

### ⚠️ Comandos do sistema

Por segurança, `executar_comando` está desativado. Para o ligar, define no `.env`:

```
JARVIS_ALLOW_SHELL=1
```

Só o faz se compreenderes o risco de deixar o assistente executar comandos.

---

## ⚙️ Configuração (`.env`)

| Variável | Omissão | Descrição |
|---|---|---|
| `JARVIS_MODEL` | `llama3.1` | Modelo do Ollama |
| `OLLAMA_HOST` | `http://localhost:11434` | Onde o Ollama está a correr |
| `JARVIS_HTTP_PORT` | `5000` | Porta do HUD web |
| `JARVIS_LANGUAGE` | `pt-PT` | Idioma da voz |
| `JARVIS_ALLOW_SHELL` | `0` | Permitir comandos do sistema |
| `JARVIS_MAX_HISTORY` | `20` | Mensagens de contexto guardadas |

---

## 🧪 Testes

```bash
pip install pytest
pytest -q
```

(Os testes não precisam do Ollama — validam memória e ferramentas.)

---

## 📁 Estrutura

```
Marley-/
├── jarvis/
│   ├── config.py        # configuração central
│   ├── brain.py         # ligação ao Ollama
│   ├── memory.py        # memória (SQLite)
│   ├── assistant.py     # orquestrador (cérebro + memória + ferramentas)
│   ├── voice.py         # voz no terminal (opcional)
│   ├── cli.py           # ponto de entrada
│   ├── tools/           # ferramentas (meteo, web, ficheiros, sistema…)
│   └── web/             # HUD holográfico (Flask + HTML/CSS/JS)
├── tests/
├── requirements.txt
└── README.md
```

---

## 🗺️ Próximos passos (ideias)

- Reconhecimento contínuo com palavra de ativação ("Jarvis…").
- Voz offline com Vosk/Piper (sem depender do browser).
- Mais ferramentas: calendário, e-mail, lembretes, controlo de casa (IoT).
- Modo "brainstorm" dedicado para desenvolver ideias passo a passo.

Feito com 💙 ao estilo Stark Industries.
