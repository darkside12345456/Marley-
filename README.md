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
  nada). No terminal há um modo de voz opcional em Python.
- **Cérebro local** — usa o Ollama, sem chaves de API nem custos por uso.
- **Memória** — lembra-se da conversa e de factos sobre ti (SQLite).
- **Ferramentas** — meteorologia, pesquisa na web, ler/escrever ficheiros,
  hora, e comandos do sistema (desligados por segurança até tu permitires).
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
| `executar_comando` | Comandos do sistema — **desligado por omissão** |

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
