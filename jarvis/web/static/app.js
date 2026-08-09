// ---- Jarvis HUD: orbe holográfico + voz no browser ----
(() => {
  const canvas = document.getElementById("orb");
  const ctx = canvas.getContext("2d");
  const stateLabel = document.getElementById("stateLabel");
  const transcript = document.getElementById("transcript");
  const dot = document.getElementById("dot");
  const statusText = document.getElementById("statusText");
  const micBtn = document.getElementById("micBtn");
  const textInput = document.getElementById("textInput");
  const sendBtn = document.getElementById("sendBtn");
  const resetBtn = document.getElementById("resetBtn");

  const STATES = {
    idle: { label: "EM ESPERA", color: "#35e6ff", speed: 0.4, amp: 0.5 },
    listening: { label: "A OUVIR", color: "#35ffa1", speed: 1.2, amp: 1.0 },
    thinking: { label: "A PENSAR", color: "#ffb84d", speed: 2.2, amp: 0.7 },
    speaking: { label: "A FALAR", color: "#35e6ff", speed: 1.6, amp: 1.3 },
  };
  let state = "idle";
  let t = 0;

  function setState(s) {
    state = s;
    stateLabel.textContent = STATES[s].label;
    stateLabel.style.color = STATES[s].color;
  }

  // ---- Animação do reator ----
  function draw() {
    const s = STATES[state];
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h / 2;
    ctx.clearRect(0, 0, w, h);
    t += s.speed * 0.02;

    // Anéis rotativos
    for (let ring = 0; ring < 3; ring++) {
      const r = 120 + ring * 45;
      const segs = 40 + ring * 10;
      ctx.beginPath();
      for (let i = 0; i <= segs; i++) {
        const a = (i / segs) * Math.PI * 2 + t * (ring % 2 ? -1 : 1) * 0.5;
        const wobble = Math.sin(a * (4 + ring) + t * 2) * 6 * s.amp;
        const rr = r + wobble;
        const x = cx + Math.cos(a) * rr;
        const y = cy + Math.sin(a) * rr;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = s.color;
      ctx.globalAlpha = 0.35 - ring * 0.07;
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // Onda de voz circular (barras radiais)
    const bars = 90;
    for (let i = 0; i < bars; i++) {
      const a = (i / bars) * Math.PI * 2;
      const noise = Math.abs(Math.sin(a * 7 + t * 3) + Math.sin(a * 3 - t * 2));
      const len = 12 + noise * 26 * s.amp;
      const inner = 92;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(a) * inner, cy + Math.sin(a) * inner);
      ctx.lineTo(cx + Math.cos(a) * (inner + len), cy + Math.sin(a) * (inner + len));
      ctx.strokeStyle = s.color;
      ctx.globalAlpha = 0.5;
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // Núcleo pulsante
    const pulse = 55 + Math.sin(t * 3) * 8 * s.amp;
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, pulse);
    grad.addColorStop(0, "#ffffff");
    grad.addColorStop(0.3, s.color);
    grad.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, pulse, 0, Math.PI * 2);
    ctx.fill();

    requestAnimationFrame(draw);
  }
  draw();
  setState("idle");

  // ---- Transcrição ----
  function addMsg(text, who) {
    const el = document.createElement("div");
    el.className = "msg " + who;
    el.textContent = text;
    transcript.appendChild(el);
    transcript.scrollTop = transcript.scrollHeight;
  }

  // ---- Voz: síntese (falar) ----
  const synth = window.speechSynthesis;
  let voices = [];
  let vozNome = localStorage.getItem("jarvisVoice") || "";
  let taxa = parseFloat(localStorage.getItem("jarvisRate") || "1.02");

  function carregarVozes() {
    voices = synth ? synth.getVoices() : [];
    const sel = document.getElementById("voiceSel");
    if (!sel) return;
    sel.innerHTML = "";
    // vozes portuguesas primeiro
    const ord = [...voices].sort((a, b) =>
      (b.lang.startsWith("pt") ? 1 : 0) - (a.lang.startsWith("pt") ? 1 : 0));
    for (const v of ord) {
      const o = document.createElement("option");
      o.value = v.name; o.textContent = `${v.name} (${v.lang})`;
      if (v.name === vozNome) o.selected = true;
      sel.appendChild(o);
    }
  }
  if (synth) { synth.onvoiceschanged = carregarVozes; carregarVozes(); }

  function speak(text) {
    if (!synth) return;
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    const v = voices.find((x) => x.name === vozNome);
    if (v) u.voice = v; else u.lang = "pt-PT";
    u.rate = taxa;
    u.pitch = 1.0;
    setState("speaking");
    u.onend = () => setState("idle");
    synth.speak(u);
  }

  // ---- Voz: reconhecimento (ouvir) ----
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let listening = false;
  if (SR) {
    recognition = new SR();
    recognition.lang = "pt-PT";
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (e) => {
      const txt = e.results[0][0].transcript;
      send(txt);
    };
    recognition.onend = () => {
      listening = false; micBtn.classList.remove("listening");
      if (state === "listening") setState("idle");
      if (wakeActive && wakeRec) { try { wakeRec.start(); } catch { /* já a correr */ } }
    };
    recognition.onerror = () => {
      listening = false; micBtn.classList.remove("listening"); setState("idle");
      if (wakeActive && wakeRec) { try { wakeRec.start(); } catch { /* já a correr */ } }
    };
  } else {
    micBtn.title = "Reconhecimento de voz não suportado neste browser";
  }

  // ---- Palavra de ativação ("Jarvis…") ----
  let wakeActive = false, wakeRec = null, nomeAtivacao = "sony";
  function startCommand() {
    if (!recognition || listening) return;
    synth && synth.cancel();
    listening = true;
    micBtn.classList.add("listening");
    setState("listening");
    try { recognition.start(); } catch { /* ignora */ }
  }
  if (SR) {
    wakeRec = new SR();
    wakeRec.lang = "pt-PT";
    wakeRec.continuous = true;
    wakeRec.interimResults = true;
    wakeRec.onresult = (e) => {
      let t = "";
      for (const r of e.results) t += r[0].transcript + " ";
      if (new RegExp(nomeAtivacao, "i").test(t) && !listening) {
        try { wakeRec.stop(); } catch { /* ignora */ }
        startCommand();
      }
    };
    wakeRec.onend = () => { if (wakeActive && !listening) { try { wakeRec.start(); } catch { /* ignora */ } } };
    wakeRec.onerror = () => {};
  }
  const wakeBtn = document.getElementById("wakeBtn");
  if (wakeBtn) wakeBtn.addEventListener("click", () => {
    if (!wakeRec) { alert("Este browser não suporta reconhecimento de voz."); return; }
    wakeActive = !wakeActive;
    wakeBtn.classList.toggle("listening", wakeActive);
    if (wakeActive) {
      try { wakeRec.start(); } catch { /* ignora */ }
      const n = document.querySelector(".brand").textContent;
      addMsg('Palavra de ativação ligada. Diz "' + n + '" e depois o teu pedido.', "bot");
    } else {
      try { wakeRec.stop(); } catch { /* ignora */ }
    }
  });

  micBtn.addEventListener("click", () => {
    if (!recognition) { alert("Este browser não suporta reconhecimento de voz. Usa o Chrome/Edge, ou escreve."); return; }
    if (listening) { recognition.stop(); return; }
    synth && synth.cancel();
    listening = true;
    micBtn.classList.add("listening");
    setState("listening");
    recognition.start();
  });

  // ---- Ações comandadas pelo Jarvis ----
  function addLink(titulo, url) {
    const a = document.createElement("a");
    a.className = "msg bot link";
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = "🔗 " + titulo;
    transcript.appendChild(a);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function addPanel(titulo, texto) {
    const el = document.createElement("div");
    el.className = "msg bot panel";
    const h = document.createElement("div");
    h.className = "panel-title";
    h.textContent = titulo;
    const pre = document.createElement("pre");
    pre.textContent = texto;
    el.appendChild(h);
    el.appendChild(pre);
    transcript.appendChild(el);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function executeActions(acoes) {
    for (const acao of acoes) {
      if (acao.tipo === "abrir_pagina") {
        const win = window.open(acao.url, "_blank", "noopener");
        if (!win) addLink(acao.titulo || acao.url, acao.url); // popup bloqueado
      } else if (acao.tipo === "modelo") {
        if (window.HoloLab) window.HoloLab.show(acao.forma, acao.peca, acao.cor, acao.escala, acao.segmentos);
      } else if (acao.tipo === "cena") {
        if (window.HoloLab) window.HoloLab.showScene(acao.partes);
      } else if (acao.tipo === "painel") {
        addPanel(acao.titulo || "Relatório", acao.texto || "");
      } else if (acao.tipo === "codigo") {
        addCode(acao.nome || "código", acao.linguagem || "", acao.codigo || "");
      }
    }
  }

  // ---- Realce de sintaxe (sem bibliotecas) ----
  const KW = new Set(("function def class return if else elif for while do end then " +
    "const let var int void float double bool char string public private protected static " +
    "import from package fn struct impl trait pub use mod match new this self super async await " +
    "yield lambda switch case break continue try catch except finally throw raise with as in is " +
    "and or not null nil none true false True False None echo print println puts val fun object " +
    "interface enum extends implements typeof instanceof export default namespace using " +
    "select insert update delete where join group order by").split(/\s+/));

  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  function highlight(code) {
    let out = "", i = 0;
    const n = code.length;
    const isW = (c) => /[A-Za-z0-9_]/.test(c);
    while (i < n) {
      const c = code[i], two = code.slice(i, i + 2);
      if (two === "//" || c === "#" || two === "--") {
        let j = i; while (j < n && code[j] !== "\n") j++;
        out += `<span class="c-com">${esc(code.slice(i, j))}</span>`; i = j;
      } else if (two === "/*") {
        let j = code.indexOf("*/", i + 2); j = j < 0 ? n : j + 2;
        out += `<span class="c-com">${esc(code.slice(i, j))}</span>`; i = j;
      } else if (c === '"' || c === "'" || c === "`") {
        let j = i + 1; while (j < n && code[j] !== c) { if (code[j] === "\\") j++; j++; }
        out += `<span class="c-str">${esc(code.slice(i, j + 1))}</span>`; i = j + 1;
      } else if (/[0-9]/.test(c)) {
        let j = i; while (j < n && /[0-9.xXa-fA-F_]/.test(code[j])) j++;
        out += `<span class="c-num">${esc(code.slice(i, j))}</span>`; i = j;
      } else if (isW(c)) {
        let j = i; while (j < n && isW(code[j])) j++;
        const w = code.slice(i, j);
        out += KW.has(w) ? `<span class="c-kw">${w}</span>` : esc(w); i = j;
      } else {
        out += esc(c); i++;
      }
    }
    return out;
  }

  function addCode(nome, linguagem, codigo) {
    const el = document.createElement("div");
    el.className = "msg bot code-card";
    const head = document.createElement("div");
    head.className = "code-head";
    head.innerHTML = `<span>💻 ${esc(nome)} · ${esc(linguagem)}</span>`;
    const copy = document.createElement("button");
    copy.textContent = "copiar";
    copy.addEventListener("click", () => { navigator.clipboard?.writeText(codigo); copy.textContent = "copiado!"; });
    head.appendChild(copy);
    const pre = document.createElement("pre");
    pre.innerHTML = highlight(codigo);
    el.appendChild(head);
    el.appendChild(pre);
    transcript.appendChild(el);
    transcript.scrollTop = transcript.scrollHeight;
  }

  // ---- Comunicação com o backend ----
  async function send(text) {
    text = (text || "").trim();
    if (!text) return;
    addMsg(text, "user");
    textInput.value = "";
    setState("thinking");
    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: text }),
      });
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let answer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop();
        for (const p of parts) {
          const line = p.replace(/^data: /, "").trim();
          if (line === "[DONE]" || !line) continue;
          const obj = JSON.parse(line);
          if (obj.erro) { answer = "Peço desculpa, ocorreu um erro: " + obj.erro; }
          else if (obj.resposta) { answer = obj.resposta; }
          if (obj.acoes) executeActions(obj.acoes);
        }
      }
      addMsg(answer, "bot");
      speak(answer);
    } catch (err) {
      const m = "Falha de ligação ao servidor.";
      addMsg(m, "bot");
      setState("idle");
    }
  }

  sendBtn.addEventListener("click", () => send(textInput.value));
  textInput.addEventListener("keydown", (e) => { if (e.key === "Enter") send(textInput.value); });
  const labBtn = document.getElementById("labBtn");
  if (labBtn) labBtn.addEventListener("click", () => {
    if (window.HoloLab) window.HoloLab.show("reator", null, window.JARVIS_PRIMARY);
  });
  const shieldBtn = document.getElementById("shieldBtn");
  if (shieldBtn) shieldBtn.addEventListener("click", () =>
    send("Faz uma auditoria de segurança completa ao meu computador."));

  // ---- Temas de cor do HUD ----
  const THEMES = {
    ciano: { p: "#35e6ff", d: "#1a8ba3" },
    verde: { p: "#35ffa1", d: "#1a8f5c" },
    dourado: { p: "#ffd24d", d: "#a37d1a" },
    stark: { p: "#ff5a5a", d: "#a33636" },
  };
  const ORDEM = ["ciano", "verde", "dourado", "stark"];
  function setTheme(nome) {
    const t = THEMES[nome] || THEMES.ciano;
    const root = document.documentElement.style;
    root.setProperty("--cyan", t.p);
    root.setProperty("--cyan-dim", t.d);
    root.setProperty("--glow", `0 0 18px ${t.p}8c`);
    STATES.idle.color = t.p;
    STATES.speaking.color = t.p;
    window.JARVIS_PRIMARY = t.p;
    localStorage.setItem("jarvisTheme", nome);
  }
  const themeBtn = document.getElementById("themeBtn");
  if (themeBtn) themeBtn.addEventListener("click", () => {
    const atual = localStorage.getItem("jarvisTheme") || "ciano";
    const prox = ORDEM[(ORDEM.indexOf(atual) + 1) % ORDEM.length];
    setTheme(prox);
    addMsg("Tema: " + prox, "bot");
  });
  setTheme(localStorage.getItem("jarvisTheme") || "ciano");

  // ---- Painel de definições ----
  const settings = document.getElementById("settings");
  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) settingsBtn.addEventListener("click", () => settings.classList.toggle("hidden"));
  const sClose = document.getElementById("settingsClose");
  if (sClose) sClose.addEventListener("click", () => settings.classList.add("hidden"));

  const voiceSel = document.getElementById("voiceSel");
  if (voiceSel) voiceSel.addEventListener("change", () => {
    vozNome = voiceSel.value; localStorage.setItem("jarvisVoice", vozNome);
  });
  const rateInput = document.getElementById("rateInput");
  if (rateInput) {
    rateInput.value = taxa;
    rateInput.addEventListener("input", () => {
      taxa = parseFloat(rateInput.value); localStorage.setItem("jarvisRate", taxa);
    });
  }
  const testVoice = document.getElementById("testVoice");
  if (testVoice) testVoice.addEventListener("click", () =>
    speak("Olá, senhor. Esta é a minha voz atual."));

  document.querySelectorAll(".tdot").forEach((b) =>
    b.addEventListener("click", () => setTheme(b.dataset.theme)));

  // ---- Gráfico do histórico de segurança ----
  const NIVEL_N = { BAIXO: 1, "MÉDIO": 2, ALTO: 3 };
  const NIVEL_COR = { BAIXO: "#35ffa1", "MÉDIO": "#ffb84d", ALTO: "#ff5a5a" };
  const histBtn = document.getElementById("histBtn");
  if (histBtn) histBtn.addEventListener("click", async () => {
    const chart = document.getElementById("histChart");
    const { historico } = await (await fetch("/api/security/history")).json();
    if (!historico || !historico.length) {
      chart.innerHTML = '<p style="opacity:.6;font-size:12px">Ainda sem histórico. Faz uma auditoria (🛡️) ou agenda verificações.</p>';
      return;
    }
    const dados = historico.slice(-24);
    let barras = "";
    for (const d of dados) {
      const n = NIVEL_N[d.nivel] || 1;
      const cor = NIVEL_COR[d.nivel] || "#35e6ff";
      barras += `<div class="hbar" title="${d.ts} — ${d.nivel}" ` +
                `style="height:${n * 30}%;background:${cor}"></div>`;
    }
    chart.innerHTML = `<div class="hbars">${barras}</div>` +
      '<div class="hleg"><span style="color:#35ffa1">■ baixo</span> ' +
      '<span style="color:#ffb84d">■ médio</span> <span style="color:#ff5a5a">■ alto</span></div>';
  });
  resetBtn.addEventListener("click", async () => {
    await fetch("/api/reset", { method: "POST" });
    transcript.innerHTML = "";
    addMsg("Memória da conversa limpa.", "bot");
  });

  // ---- Estado / ligação ----
  async function checkStatus() {
    try {
      const r = await fetch("/api/status");
      const s = await r.json();
      if (s.nome) {
        document.querySelector(".brand").textContent = s.nome.toUpperCase();
        document.title = s.nome;
        nomeAtivacao = s.nome.toLowerCase();
      }
      if (s.ollama_ativo) {
        dot.className = "dot online";
        statusText.textContent = `online · ${s.modelo}`;
      } else {
        dot.className = "dot offline";
        statusText.textContent = "Ollama offline";
      }
    } catch {
      dot.className = "dot offline";
      statusText.textContent = "sem servidor";
    }
  }
  checkStatus();
  setInterval(checkStatus, 8000);

  // ---- Monitorização de segurança automática (se agendada) ----
  let ultimaSegTs = null;
  async function checkSecurity() {
    try {
      const r = await fetch("/api/security/last");
      const s = await r.json();
      if (s.ativo && s.ultima && s.ultima.ts !== ultimaSegTs) {
        ultimaSegTs = s.ultima.ts;
        if (s.ultima.nivel && s.ultima.nivel !== "BAIXO") {
          addPanel("🛡️ Alerta de segurança automático", s.ultima.relatorio || "");
          speak("Atenção, senhor. A verificação automática detetou algo que merece atenção.");
        }
      }
    } catch { /* ignora */ }
  }
  checkSecurity();
  setInterval(checkSecurity, 30000);

  // Saudação inicial
  setTimeout(() => {
    const hi = "Sistemas online. Bom dia, senhor. Em que posso ajudar?";
    addMsg(hi, "bot");
    speak(hi);
  }, 900);
})();
