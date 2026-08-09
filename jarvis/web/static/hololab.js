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
  let editor = false, selectedIndex = -1, moving = false, corAtual = "#35e6ff";
  let history = [], hp = -1, snap = false;
  const GRID = 0.5;
  function snapVal(v) { return snap ? Math.round(v / GRID) * GRID : v; }

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

    // grelha do chão (modo editor)
    if (editor) {
      ctx.strokeStyle = "rgba(53,230,255,.18)";
      ctx.lineWidth = 1; ctx.shadowBlur = 0; ctx.globalAlpha = 1;
      for (let g = -3; g <= 3; g += GRID) {
        const a1 = projeta([g, 0, -3], cx, cy, zoom), a2 = projeta([g, 0, 3], cx, cy, zoom);
        const b1 = projeta([-3, 0, g], cx, cy, zoom), b2 = projeta([3, 0, g], cx, cy, zoom);
        ctx.beginPath(); ctx.moveTo(a1[0], a1[1]); ctx.lineTo(a2[0], a2[1]); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(b1[0], b1[1]); ctx.lineTo(b2[0], b2[1]); ctx.stroke();
      }
    }

    for (const inst of instancias) {
      const trans = (p) => {
        const r = aplicarRot(p, inst.rot || [0, 0, 0]);
        return [r[0] * inst.escala + inst.pos[0],
                r[1] * inst.escala + inst.pos[1],
                r[2] * inst.escala + inst.pos[2]];
      };
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

  function _inst(forma, cor, escala, segmentos, pos, rot) {
    const m = construir(forma, segmentos);
    return { v: m.v, e: m.e, forma, seg: segmentos || 0, cor: cor || primaria(),
             escala: escala || 1, pos: pos ? pos.slice() : [0, 0, 0],
             rot: rot ? rot.slice() : [0, 0, 0] };
  }
  function primaria() { return window.JARVIS_PRIMARY || "#35e6ff"; }

  function aplicarRot(p, rot) {
    let [x, y, z] = p;
    const [rx, ry, rz] = rot;
    let y1 = y * Math.cos(rx) - z * Math.sin(rx), z1 = y * Math.sin(rx) + z * Math.cos(rx);
    y = y1; z = z1;
    let x2 = x * Math.cos(ry) + z * Math.sin(ry), z2 = -x * Math.sin(ry) + z * Math.cos(ry);
    x = x2; z = z2;
    let x3 = x * Math.cos(rz) - y * Math.sin(rz), y3 = x * Math.sin(rz) + y * Math.cos(rz);
    return [x3, y3, z];
  }

  function abrir() {
    panel.classList.remove("hidden");
    if (!running) { running = true; frame(); }
  }

  function serialize() {
    return instancias.map((i) => ({ forma: i.forma, cor: i.cor, escala: i.escala,
                                    segmentos: i.seg, pos: i.pos, rot: i.rot }));
  }

  function syncScene() {
    fetch("/api/scene/current", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ partes: serialize() }),
    }).catch(() => {});
  }

  // ---- Histórico (undo/redo) ----
  function pushHistory() {
    history = history.slice(0, hp + 1);
    history.push(serialize());
    if (history.length > 60) history.shift();
    hp = history.length - 1;
  }
  function resetHistory() { history = []; hp = -1; pushHistory(); }
  function rebuild(partes) {
    instancias = partes.map((p) => _inst(p.forma, p.cor, p.escala, p.segmentos, p.pos, p.rot));
    selectedIndex = -1;
  }
  function undo() {
    if (hp <= 0) return;
    hp--; rebuild(history[hp]); title.textContent = "↶ DESFEITO"; syncScene();
  }
  function redo() {
    if (hp >= history.length - 1) return;
    hp++; rebuild(history[hp]); title.textContent = "↷ REFEITO"; syncScene();
  }
  function commit() { pushHistory(); syncScene(); }

  function show(forma, peca, cor, escala, segmentos) {
    const f = NOMES[forma] ? forma : "reator";
    instancias = [_inst(f, cor, escala, segmentos, [0, 0, 0])];
    selectedIndex = -1;
    title.textContent = (peca && String(peca).toUpperCase()) || NOMES[f] || f.toUpperCase();
    abrir();
    resetHistory();
    syncScene();
  }

  function showScene(partes) {
    if (!partes || !partes.length) return;
    instancias = partes.map((p) => _inst(p.forma, p.cor, p.escala, p.segmentos, p.pos, p.rot));
    selectedIndex = -1;
    title.textContent = "CENA (" + partes.length + " peças)";
    abrir();
    resetHistory();
    syncScene();
  }

  function hide() { running = false; panel.classList.add("hidden"); }

  // ---- Editor: adicionar / remover peças ----
  function addPiece(forma) {
    const f = NOMES[forma] ? forma : "reator";
    const pos = [(Math.random() - 0.5) * 1.6, 0, (Math.random() - 0.5) * 1.6];
    if (snap) { pos[0] = snapVal(pos[0]); pos[2] = snapVal(pos[2]); }
    instancias.push(_inst(f, corAtual, 1, 0, pos));
    selectedIndex = instancias.length - 1;
    title.textContent = "EDITOR (" + instancias.length + " peças)";
    abrir();
    commit();
  }
  function duplicateSelected() {
    if (selectedIndex < 0) return;
    const s = instancias[selectedIndex];
    const pos = [clamp(s.pos[0] + 0.5), s.pos[1], clamp(s.pos[2] + 0.5)];
    instancias.push(_inst(s.forma, s.cor, s.escala, s.seg, pos, s.rot));
    selectedIndex = instancias.length - 1;
    commit();
  }
  function scaleSel(f) {
    if (selectedIndex < 0) return;
    const i = instancias[selectedIndex];
    i.escala = Math.max(0.2, Math.min(3, i.escala * f));
    commit();
  }
  function rotSel(eixo, delta) {
    if (selectedIndex < 0) return;
    instancias[selectedIndex].rot[eixo] += delta;
    commit();
  }
  function alinhar() {
    if (!instancias.length) return;
    for (const i of instancias) {
      i.pos = [Math.round(i.pos[0] / GRID) * GRID,
               Math.round(i.pos[1] / GRID) * GRID,
               Math.round(i.pos[2] / GRID) * GRID];
    }
    commit();
  }
  function setSnap(on) {
    snap = !!on;
    const b = document.getElementById("holoSnap");
    if (b) b.classList.toggle("ativo", snap);
  }
  function removeSelected() {
    if (selectedIndex < 0) return;
    instancias.splice(selectedIndex, 1);
    selectedIndex = -1;
    commit();
  }
  function setColor(hex) {
    corAtual = hex;
    if (editor && selectedIndex >= 0) {
      instancias[selectedIndex].cor = hex;
      commit();
    }
  }

  // ---- Exportar para .obj (sólido combinado, gerado no servidor) ----
  async function exportOBJ() {
    if (!instancias.length) return;
    const r = await fetch("/api/scene/export", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ partes: serialize() }),
    });
    baixar(await r.text(), (instancias.length === 1 ? instancias[0].forma : "cena") + ".obj");
  }
  function baixar(texto, nome) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([texto], { type: "text/plain" }));
    a.download = nome;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  // ---- Guardar / carregar projetos (com miniaturas) ----
  function miniatura() {
    // reduz o canvas atual a uma miniatura 200x200 (dataURL PNG)
    try {
      const off = document.createElement("canvas");
      off.width = 200; off.height = 200;
      off.getContext("2d").drawImage(canvas, 0, 0, 200, 200);
      return off.toDataURL("image/png");
    } catch { return null; }
  }
  async function guardar() {
    if (!instancias.length) { alert("Nada para guardar."); return; }
    const nome = prompt("Nome do projeto 3D:");
    if (!nome) return;
    await fetch("/api/scene/save", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, partes: serialize(), thumb: miniatura() }),
    });
    title.textContent = "GUARDADO: " + nome.toUpperCase();
  }
  async function refreshGallery() {
    const grid = document.getElementById("galleryGrid");
    const gallery = document.getElementById("holoGallery");
    const { projetos } = await (await fetch("/api/scene/list")).json();
    grid.innerHTML = "";
    if (!projetos || !projetos.length) {
      grid.innerHTML = '<p style="opacity:.6">Ainda não há projetos guardados.</p>';
      gallery.classList.remove("hidden");
      return;
    }
    for (const p of projetos) {
      const card = document.createElement("div");
      card.className = "gallery-card";
      const img = document.createElement(p.thumb ? "img" : "div");
      if (p.thumb) img.src = "/api/scene/thumb/" + encodeURIComponent(p.nome) + "?t=" + Date.now();
      else { img.className = "no-thumb"; img.textContent = "3D"; }
      const lbl = document.createElement("span");
      lbl.textContent = p.nome;
      const acts = document.createElement("div");
      acts.className = "card-acts";
      const bR = document.createElement("button"); bR.textContent = "✎"; bR.title = "Renomear";
      const bD = document.createElement("button"); bD.textContent = "🗑"; bD.title = "Apagar";
      bR.addEventListener("click", async (e) => {
        e.stopPropagation();
        const novo = prompt("Novo nome:", p.nome);
        if (!novo || novo === p.nome) return;
        const r = await postJSON("/api/scene/rename", { nome: p.nome, novo });
        if (r.erro) alert(r.erro); else refreshGallery();
      });
      bD.addEventListener("click", async (e) => {
        e.stopPropagation();
        if (!confirm(`Apagar o projeto "${p.nome}"?`)) return;
        await postJSON("/api/scene/delete", { nome: p.nome });
        refreshGallery();
      });
      acts.appendChild(bR); acts.appendChild(bD);
      card.appendChild(img);
      card.appendChild(lbl);
      card.appendChild(acts);
      card.addEventListener("click", async () => {
        const res = await (await fetch("/api/scene/load?nome=" + encodeURIComponent(p.nome))).json();
        gallery.classList.add("hidden");
        if (res.ok) showScene(res.partes); else alert(res.erro || "Erro.");
      });
      grid.appendChild(card);
    }
    gallery.classList.remove("hidden");
  }
  function postJSON(url, body) {
    return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(body) }).then((r) => r.json());
  }
  async function carregar() { refreshGallery(); }

  window.HoloLab = { show, showScene, hide, setSnap };

  // ---- Ligações de botões ----
  const on = (id, fn) => { const b = document.getElementById(id); if (b) b.addEventListener("click", fn); };
  on("holoClose", hide);
  on("holoExport", exportOBJ);
  on("holoAdd", () => addPiece(sel ? sel.value : "reator"));
  on("holoDup", duplicateSelected);
  on("holoRemove", removeSelected);
  on("holoUndo", undo);
  on("holoRedo", redo);
  on("holoScaleDown", () => scaleSel(0.85));
  on("holoScaleUp", () => scaleSel(1.18));
  on("holoRotY", () => rotSel(1, 0.26));
  on("holoRotX", () => rotSel(0, 0.26));
  on("holoSnap", () => setSnap(!snap));
  on("holoAlign", alinhar);
  window.addEventListener("keydown", (e) => {
    if (panel.classList.contains("hidden")) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
      e.preventDefault(); e.shiftKey ? redo() : undo();
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
      e.preventDefault(); redo();
    } else if (editor && selectedIndex >= 0) {
      if (e.key === "[") scaleSel(0.85);
      else if (e.key === "]") scaleSel(1.18);
      else if (e.key === ",") rotSel(1, -0.26);
      else if (e.key === ".") rotSel(1, 0.26);
      else if (e.key === ";") rotSel(0, -0.26);
      else if (e.key === "'") rotSel(0, 0.26);
    }
  });
  on("holoSave", guardar);
  on("holoLoad", carregar);
  on("galleryClose", () => document.getElementById("holoGallery").classList.add("hidden"));
  const corInput = document.getElementById("holoColor");
  if (corInput) corInput.addEventListener("input", () => setColor(corInput.value));
  on("holoEdit", () => {
    editor = !editor;
    const b = document.getElementById("holoEdit");
    if (b) b.classList.toggle("ativo", editor);
    title.textContent = editor ? "MODO EDITOR" : "HOLO-LAB";
  });
  const sel = document.getElementById("holoSelect");
  if (sel) sel.addEventListener("change", () => { if (!editor) show(sel.value, null, primaria()); });

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
      if (best >= 0) {
        selectedIndex = best; moving = true;
        const ci = document.getElementById("holoColor");
        if (ci) ci.value = instancias[best].cor;
        corAtual = instancias[best].cor;
        return;
      }
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
    if (moving) {
      if (snap && selectedIndex >= 0) {
        const p = instancias[selectedIndex].pos;
        p[0] = snapVal(p[0]); p[1] = snapVal(p[1]); p[2] = snapVal(p[2]);
      }
      commit();
    }
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
