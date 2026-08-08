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
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
    requestAnimationFrame(frame);
  }

  function _inst(forma, cor, escala, segmentos, pos) {
    const m = construir(forma, segmentos);
    return { v: m.v, e: m.e, cor: cor || "#35e6ff", escala: escala || 1, pos: pos || [0, 0, 0] };
  }

  function abrir() {
    panel.classList.remove("hidden");
    if (!running) { running = true; frame(); }
  }

  function show(forma, peca, cor, escala, segmentos) {
    const f = NOMES[forma] ? forma : "reator";
    instancias = [_inst(f, cor, escala, segmentos, [0, 0, 0])];
    title.textContent = (peca && String(peca).toUpperCase()) || NOMES[f] || f.toUpperCase();
    abrir();
  }

  function showScene(partes) {
    if (!partes || !partes.length) return;
    instancias = partes.map((p) =>
      _inst(p.forma, p.cor, p.escala, p.segmentos, p.pos));
    title.textContent = "CENA (" + partes.length + " peças)";
    abrir();
  }

  function hide() { running = false; panel.classList.add("hidden"); }

  // ---- Exportar o que está no ecrã para .obj (wireframe) ----
  function exportOBJ() {
    if (!instancias.length) return;
    const out = ["# Exportado pelo Jarvis Holo-Lab"];
    let offset = 0;
    instancias.forEach((inst, ii) => {
      out.push("o parte" + (ii + 1));
      for (const p of inst.v) {
        const x = p[0] * inst.escala + inst.pos[0];
        const y = p[1] * inst.escala + inst.pos[1];
        const z = p[2] * inst.escala + inst.pos[2];
        out.push(`v ${x.toFixed(5)} ${y.toFixed(5)} ${z.toFixed(5)}`);
      }
      for (const [a, b] of inst.e) out.push(`l ${a + 1 + offset} ${b + 1 + offset}`);
      offset += inst.v.length;
    });
    const blob = new Blob([out.join("\n") + "\n"], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "holo-lab.obj";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  window.HoloLab = { show, showScene, hide };

  document.getElementById("holoClose").addEventListener("click", hide);
  const expBtn = document.getElementById("holoExport");
  if (expBtn) expBtn.addEventListener("click", exportOBJ);
  const sel = document.getElementById("holoSelect");
  if (sel) sel.addEventListener("change", () => show(sel.value, null, "#35e6ff"));

  // ---- Controlo por rato/toque: rodar e zoom ----
  function pointerDown(e) {
    dragging = true;
    px = e.clientX ?? e.touches[0].clientX;
    py = e.clientY ?? e.touches[0].clientY;
  }
  function pointerMove(e) {
    if (!dragging) return;
    const x = e.clientX ?? e.touches[0].clientX;
    const y = e.clientY ?? e.touches[0].clientY;
    ang += (x - px) * 0.01;
    tilt = Math.max(-1.4, Math.min(1.4, tilt + (y - py) * 0.01));
    px = x; py = y;
  }
  function pointerUp() { dragging = false; }

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
