// ---- Holo-Lab: motor 3D wireframe (sem dependências) ----
// Desenha peças em wireframe holográfico a rodar, estilo "desenho do fato".
// Suporta tamanho, detalhe (segmentos), cor e cenas com várias peças.
(() => {
  const canvas = document.getElementById("holoCanvas");
  const panel = document.getElementById("holoLab");
  const title = document.getElementById("holoTitle");
  const ctx = canvas.getContext("2d");

  // ---- Construtores de malha: devolvem {v:[[x,y,z]], e:[[i,j]]} ----
  function esfera(seg = 16, ring = 12, R = 1) {
    const v = [], e = [];
    for (let i = 0; i <= ring; i++) {
      const lat = -Math.PI / 2 + (i / ring) * Math.PI;
      for (let j = 0; j < seg; j++) {
        const lon = (j / seg) * Math.PI * 2;
        v.push([R * Math.cos(lat) * Math.cos(lon), R * Math.sin(lat), R * Math.cos(lat) * Math.sin(lon)]);
      }
    }
    const idx = (i, j) => i * seg + (j % seg);
    for (let i = 0; i <= ring; i++)
      for (let j = 0; j < seg; j++) {
        e.push([idx(i, j), idx(i, j + 1)]);
        if (i < ring) e.push([idx(i, j), idx(i + 1, j)]);
      }
    return { v, e };
  }

  function toroide(R = 0.85, r = 0.35, seg = 28, side = 12) {
    const v = [], e = [];
    for (let i = 0; i < seg; i++) {
      const u = (i / seg) * Math.PI * 2;
      for (let j = 0; j < side; j++) {
        const w = (j / side) * Math.PI * 2;
        v.push([(R + r * Math.cos(w)) * Math.cos(u), r * Math.sin(w), (R + r * Math.cos(w)) * Math.sin(u)]);
      }
    }
    const idx = (i, j) => (i % seg) * side + (j % side);
    for (let i = 0; i < seg; i++)
      for (let j = 0; j < side; j++) {
        e.push([idx(i, j), idx(i + 1, j)]);
        e.push([idx(i, j), idx(i, j + 1)]);
      }
    return { v, e };
  }

  function cilindro(R = 0.7, h = 1.4, seg = 20, rings = 5) {
    const v = [], e = [];
    for (let k = 0; k <= rings; k++) {
      const y = -h / 2 + (k / rings) * h;
      for (let j = 0; j < seg; j++) {
        const a = (j / seg) * Math.PI * 2;
        v.push([R * Math.cos(a), y, R * Math.sin(a)]);
      }
    }
    const idx = (k, j) => k * seg + (j % seg);
    for (let k = 0; k <= rings; k++)
      for (let j = 0; j < seg; j++) {
        e.push([idx(k, j), idx(k, j + 1)]);
        if (k < rings) e.push([idx(k, j), idx(k + 1, j)]);
      }
    return { v, e };
  }

  function estrutura(n = 3, s = 1.2) {
    const v = [], e = [], at = {};
    const step = (2 * s) / n;
    let id = 0;
    for (let i = 0; i <= n; i++)
      for (let j = 0; j <= n; j++)
        for (let k = 0; k <= n; k++) {
          at[`${i},${j},${k}`] = id++;
          v.push([-s + i * step, -s + j * step, -s + k * step]);
        }
    const link = (a, b) => e.push([at[a], at[b]]);
    for (let i = 0; i <= n; i++)
      for (let j = 0; j <= n; j++)
        for (let k = 0; k <= n; k++) {
          if (i < n) link(`${i},${j},${k}`, `${i + 1},${j},${k}`);
          if (j < n) link(`${i},${j},${k}`, `${i},${j + 1},${k}`);
          if (k < n) link(`${i},${j},${k}`, `${i},${j},${k + 1}`);
        }
    return { v, e };
  }

  function reator(seg = 36) {
    const v = [], e = [];
    const raios = [0.35, 0.6, 0.9, 1.05];
    raios.forEach((R, ri) => {
      const base = v.length;
      for (let j = 0; j < seg; j++) {
        const a = (j / seg) * Math.PI * 2;
        v.push([R * Math.cos(a), 0, R * Math.sin(a)]);
      }
      for (let j = 0; j < seg; j++) e.push([base + j, base + ((j + 1) % seg)]);
      if (ri === 1) {
        const outer = v.length;
        for (let j = 0; j < 10; j++) {
          const a = (j / 10) * Math.PI * 2;
          v.push([0.6 * Math.cos(a), 0, 0.6 * Math.sin(a)]);
          v.push([0.9 * Math.cos(a), 0, 0.9 * Math.sin(a)]);
          e.push([outer + j * 2, outer + j * 2 + 1]);
        }
      }
    });
    const flat = v.length;
    for (let i = 0; i < flat; i++) v.push([v[i][0], 0.12, v[i][2]]);
    return { v, e };
  }

  function capacete(seg = 18) {
    const { v, e } = esfera(seg, 10, 1);
    const keepV = [], map = {}, ne = [];
    v.forEach((p, i) => {
      if (p[1] > -0.35) { map[i] = keepV.length; keepV.push([p[0], p[1] * 1.15, p[2] * 0.92]); }
    });
    e.forEach(([a, b]) => { if (a in map && b in map) ne.push([map[a], map[b]]); });
    const eye = keepV.length;
    keepV.push([-0.42, 0.05, 0.85], [-0.12, 0.05, 0.95], [0.12, 0.05, 0.95], [0.42, 0.05, 0.85]);
    ne.push([eye, eye + 1], [eye + 2, eye + 3]);
    return { v: keepV, e: ne };
  }

  // Constrói uma malha a partir da forma + nº de segmentos (detalhe).
  function construir(forma, seg) {
    const s = seg && seg >= 6 ? seg : null;
    switch (forma) {
      case "esfera": return esfera(s || 18, 12);
      case "toroide": return toroide(0.85, 0.35, s || 28, 12);
      case "cilindro": return cilindro(0.7, 1.4, s || 20, 5);
      case "manopla": return cilindro(0.55, 1.5, s || 16, 7);
      case "estrutura": return estrutura(s ? Math.min(6, Math.round(s / 6)) : 3);
      case "capacete": return capacete(s || 18);
      case "reator":
      default: return reator(s || 36);
    }
  }

  const NOMES = {
    reator: "REATOR ARC", capacete: "CAPACETE", manopla: "MANOPLA",
    esfera: "NÚCLEO", toroide: "ANEL DE ENERGIA", cilindro: "MOTOR", estrutura: "ESTRUTURA",
  };

  // instancias: [{v, e, cor, escala, pos:[x,y,z]}]
  let instancias = [], ang = 0, tilt = 0.5, running = false;
  let zoomFactor = 1, autoRotate = true, dragging = false, px = 0, py = 0;
  let editor = false, selectedIndex = -1, moving = false;

  function projeta(p, cx, cy, zoom) {
    let [x, y, z] = p;
    const x1 = x * Math.cos(ang) - z * Math.sin(ang);
    const z1 = x * Math.sin(ang) + z * Math.cos(ang);
    const y1 = y * Math.cos(tilt) - z1 * Math.sin(tilt);
    const z2 = y * Math.sin(tilt) + z1 * Math.cos(tilt);
    const fov = 4.5, scale = (fov / (fov + z2)) * zoom;
    return [cx + x1 * scale, cy - y1 * scale, z2];
  }

  function frame() {
    if (!running || !instancias.length) return;
    const w = canvas.width, h = canvas.height, cx = w / 2, cy = h / 2, zoom = w * 0.3 * zoomFactor;
    ctx.clearRect(0, 0, w, h);
    if (autoRotate && !dragging) ang += 0.012;

    for (const inst of instancias) {
      const trans = (p) => [
        p[0] * inst.escala + inst.pos[0],
        p[1] * inst.escala + inst.pos[1],
        p[2] * inst.escala + inst.pos[2],
      ];
      ctx.lineWidth = 1.3;
      ctx.strokeStyle = inst.cor;
      ctx.shadowColor = inst.cor;
      for (const [a, b] of inst.e) {
        const pa = projeta(trans(inst.v[a]), cx, cy, zoom);
        const pb = projeta(trans(inst.v[b]), cx, cy, zoom);
        const depth = (pa[2] + pb[2]) / 2;
        ctx.globalAlpha = Math.min(1, Math.max(0.15, 0.75 + depth * 0.1));
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.moveTo(pa[0], pa[1]);
        ctx.lineTo(pb[0], pb[1]);
        ctx.stroke();
      }
      ctx.shadowBlur = 6;
      ctx.fillStyle = "#eafcff";
      for (const p of inst.v) {
        const pp = projeta(trans(p), cx, cy, zoom);
        ctx.globalAlpha = 0.9;
        ctx.beginPath();
        ctx.arc(pp[0], pp[1], 1.6, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    // realce da peça selecionada (modo editor)
    if (editor && selectedIndex >= 0 && instancias[selectedIndex]) {
      const c = projeta(instancias[selectedIndex].pos, cx, cy, zoom);
      ctx.strokeStyle = "#ffd24d";
      ctx.shadowColor = "#ffd24d";
      ctx.shadowBlur = 12;
      ctx.globalAlpha = 0.95;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(c[0], c[1], 30, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
    requestAnimationFrame(frame);
  }

  function centroEcra(inst) {
    const w = canvas.width, h = canvas.height;
    return projeta(inst.pos, w / 2, h / 2, w * 0.3 * zoomFactor);
  }

  function _inst(forma, cor, escala, segmentos, pos) {
    const m = construir(forma, segmentos);
    return { v: m.v, e: m.e, forma, seg: segmentos || 0, cor: cor || "#35e6ff",
             escala: escala || 1, pos: pos ? pos.slice() : [0, 0, 0] };
  }

  function abrir() {
    panel.classList.remove("hidden");
    if (!running) { running = true; frame(); }
  }

  function serialize() {
    return instancias.map((i) => ({ forma: i.forma, cor: i.cor, escala: i.escala,
                                    segmentos: i.seg, pos: i.pos }));
  }

  function syncScene() {
    fetch("/api/scene/current", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ partes: serialize() }),
    }).catch(() => {});
  }

  function show(forma, peca, cor, escala, segmentos) {
    const f = NOMES[forma] ? forma : "reator";
    instancias = [_inst(f, cor, escala, segmentos, [0, 0, 0])];
    selectedIndex = -1;
    title.textContent = (peca && String(peca).toUpperCase()) || NOMES[f] || f.toUpperCase();
    abrir();
    syncScene();
  }

  function showScene(partes) {
    if (!partes || !partes.length) return;
    instancias = partes.map((p) => _inst(p.forma, p.cor, p.escala, p.segmentos, p.pos));
    selectedIndex = -1;
    title.textContent = "CENA (" + partes.length + " peças)";
    abrir();
    syncScene();
  }

  function hide() { running = false; panel.classList.add("hidden"); }

  // ---- Editor: adicionar / remover peças ----
  function addPiece(forma) {
    const f = NOMES[forma] ? forma : "reator";
    const pos = [(Math.random() - 0.5) * 1.6, 0, (Math.random() - 0.5) * 1.6];
    instancias.push(_inst(f, "#35e6ff", 1, 0, pos));
    selectedIndex = instancias.length - 1;
    title.textContent = "EDITOR (" + instancias.length + " peças)";
    abrir();
    syncScene();
  }
  function removeSelected() {
    if (selectedIndex < 0) return;
    instancias.splice(selectedIndex, 1);
    selectedIndex = -1;
    syncScene();
  }

  // ---- Exportar para .obj ----
  async function exportOBJ() {
    if (!instancias.length) return;
    if (instancias.length === 1 && NOMES[instancias[0].forma]) {
      // sólido fechado gerado no servidor (imprimível)
      const i = instancias[0];
      const url = `/api/export/${i.forma}?escala=${i.escala}&segmentos=${i.seg}`;
      const r = await fetch(url);
      const txt = await r.text();
      baixar(txt, i.forma + ".obj");
      return;
    }
    // cena com várias peças: exporta o wireframe combinado
    const out = ["# Exportado pelo Jarvis Holo-Lab"];
    let offset = 0;
    instancias.forEach((inst, ii) => {
      out.push("o parte" + (ii + 1));
      for (const p of inst.v) {
        out.push(`v ${(p[0] * inst.escala + inst.pos[0]).toFixed(5)} ` +
                 `${(p[1] * inst.escala + inst.pos[1]).toFixed(5)} ` +
                 `${(p[2] * inst.escala + inst.pos[2]).toFixed(5)}`);
      }
      for (const [a, b] of inst.e) out.push(`l ${a + 1 + offset} ${b + 1 + offset}`);
      offset += inst.v.length;
    });
    baixar(out.join("\n") + "\n", "holo-lab.obj");
  }
  function baixar(texto, nome) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([texto], { type: "text/plain" }));
    a.download = nome;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  // ---- Guardar / carregar projetos ----
  async function guardar() {
    const nome = prompt("Nome do projeto 3D:");
    if (!nome) return;
    await fetch("/api/scene/save", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, partes: serialize() }),
    });
    title.textContent = "GUARDADO: " + nome.toUpperCase();
  }
  async function carregar() {
    const r = await fetch("/api/scene/list");
    const { projetos } = await r.json();
    if (!projetos || !projetos.length) { alert("Ainda não há projetos guardados."); return; }
    const nome = prompt("Carregar qual?\n" + projetos.join(", "), projetos[0]);
    if (!nome) return;
    const res = await (await fetch("/api/scene/load?nome=" + encodeURIComponent(nome))).json();
    if (res.ok) showScene(res.partes); else alert(res.erro || "Não encontrado.");
  }

  window.HoloLab = { show, showScene, hide };

  // ---- Ligações de botões ----
  const on = (id, fn) => { const b = document.getElementById(id); if (b) b.addEventListener("click", fn); };
  on("holoClose", hide);
  on("holoExport", exportOBJ);
  on("holoAdd", () => addPiece(sel ? sel.value : "reator"));
  on("holoRemove", removeSelected);
  on("holoSave", guardar);
  on("holoLoad", carregar);
  on("holoEdit", () => {
    editor = !editor;
    const b = document.getElementById("holoEdit");
    if (b) b.classList.toggle("ativo", editor);
    title.textContent = editor ? "MODO EDITOR" : "HOLO-LAB";
  });
  const sel = document.getElementById("holoSelect");
  if (sel) sel.addEventListener("change", () => { if (!editor) show(sel.value, null, "#35e6ff"); });

  // ---- Controlo por rato/toque: rodar, mover peças, zoom ----
  function toCanvas(e) {
    const r = canvas.getBoundingClientRect();
    const cx = (e.clientX ?? e.touches[0].clientX);
    const cy = (e.clientY ?? e.touches[0].clientY);
    const s = canvas.width / r.width;
    return { x: (cx - r.left) * s, y: (cy - r.top) * s, cx, cy };
  }

  function pointerDown(e) {
    const c = toCanvas(e);
    px = c.cx; py = c.cy;
    if (editor) {
      // seleciona a peça mais próxima do clique
      let best = -1, bd = 40;
      instancias.forEach((inst, i) => {
        const s = centroEcra(inst);
        const d = Math.hypot(s[0] - c.x, s[1] - c.y);
        if (d < bd) { bd = d; best = i; }
      });
      if (best >= 0) { selectedIndex = best; moving = true; return; }
      selectedIndex = -1;
    }
    dragging = true;
  }
  function pointerMove(e) {
    if (!moving && !dragging) return;
    const cx = (e.clientX ?? e.touches[0].clientX);
    const cy = (e.clientY ?? e.touches[0].clientY);
    const s = canvas.width / canvas.getBoundingClientRect().width;
    const cdx = (cx - px) * s, cdy = (cy - py) * s;
    px = cx; py = cy;
    if (moving && selectedIndex >= 0) {
      const zoom = canvas.width * 0.3 * zoomFactor;
      const u = cdx / zoom;
      const inst = instancias[selectedIndex];
      inst.pos[0] = clamp(inst.pos[0] + Math.cos(ang) * u);
      inst.pos[2] = clamp(inst.pos[2] - Math.sin(ang) * u);
      inst.pos[1] = clamp(inst.pos[1] - cdy / (zoom * Math.max(0.3, Math.cos(tilt))));
    } else if (dragging) {
      ang += cdx * 0.01;
      tilt = Math.max(-1.4, Math.min(1.4, tilt + cdy * 0.01));
    }
  }
  function clamp(v) { return Math.max(-3, Math.min(3, v)); }
  function pointerUp() {
    if (moving) syncScene();
    moving = false; dragging = false;
  }

  canvas.addEventListener("mousedown", pointerDown);
  window.addEventListener("mousemove", pointerMove);
  window.addEventListener("mouseup", pointerUp);
  canvas.addEventListener("touchstart", pointerDown, { passive: true });
  canvas.addEventListener("touchmove", pointerMove, { passive: true });
  canvas.addEventListener("touchend", pointerUp);
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    zoomFactor = Math.max(0.4, Math.min(3, zoomFactor * (e.deltaY < 0 ? 1.1 : 0.9)));
  }, { passive: false });
})();
