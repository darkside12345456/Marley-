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
  function speak(text) {
    if (!synth) return;
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "pt-PT";
    u.rate = 1.02;
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
    recognition.onend = () => { listening = false; micBtn.classList.remove("listening"); if (state === "listening") setState("idle"); };
    recognition.onerror = () => { listening = false; micBtn.classList.remove("listening"); setState("idle"); };
  } else {
    micBtn.title = "Reconhecimento de voz não suportado neste browser";
  }

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

  function executeActions(acoes) {
    for (const acao of acoes) {
      if (acao.tipo === "abrir_pagina") {
        const win = window.open(acao.url, "_blank", "noopener");
        // se o browser bloquear o popup, deixa um link clicável
        if (!win) addLink(acao.titulo || acao.url, acao.url);
      } else if (acao.tipo === "modelo") {
        if (window.HoloLab) window.HoloLab.show(acao.forma, acao.peca, acao.cor);
      }
    }
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
    if (window.HoloLab) window.HoloLab.show("reator", null, "#35e6ff");
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

  // Saudação inicial
  setTimeout(() => {
    const hi = "Sistemas online. Bom dia, senhor. Em que posso ajudar?";
    addMsg(hi, "bot");
    speak(hi);
  }, 900);
})();
