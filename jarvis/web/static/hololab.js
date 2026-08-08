// ---- Holo-Lab: motor 3D wireframe (sem dependências) ----
// Desenha peças em wireframe holográfico a rodar, estilo "desenho do fato".
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
        if (j < seg) e.push([idx(i, j), idx(i, j + 1)]);
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
    const v = [], e = [];
    const step = (2 * s) / n;
    const at = {};
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

  // Reator: anéis concêntricos planos + raios (o clássico arc reactor).
  function reator() {
    const v = [], e = [];
    const raios = [0.35, 0.6, 0.9, 1.05];
    const seg = 36;
    raios.forEach((R, ri) => {
      const base = v.length;
      for (let j = 0; j < seg; j++) {
        const a = (j / seg) * Math.PI * 2;
        v.push([R * Math.cos(a), 0, R * Math.sin(a)]);
      }
      for (let j = 0; j < seg; j++) e.push([base + j, base + ((j + 1) % seg)]);
      // raios ligando anel interno e externo
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
    // ligeira espessura (dois planos)
    const flat = v.length;
    for (let i = 0; i < flat; i++) v.push([v[i][0], 0.12, v[i][2]]);
    return { v, e };
  }

  // Capacete: cúpula (meia esfera) + linha do maxilar + duas "fendas" de olhos.
  function capacete() {
    const { v, e } = esfera(18, 10, 1);
    const keepV = [], map = {}, ne = [];
    v.forEach((p, i) => {
      if (p[1] > -0.35) { map[i] = keepV.length; keepV.push([p[0], p[1] * 1.15, p[2] * 0.92]); }
    });
    e.forEach(([a, b]) => { if (a in map && b in map) ne.push([map[a], map[b]]); });
    // fendas dos olhos
    const eye = keepV.length;
    keepV.push([-0.42, 0.05, 0.85], [-0.12, 0.05, 0.95], [0.12, 0.05, 0.95], [0.42, 0.05, 0.85]);
    ne.push([eye, eye + 1], [eye + 2, eye + 3]);
    return { v: keepV, e: ne };
  }

  const BUILDERS = {
    esfera: () => esfera(18, 12),
    toroide: () => toroide(),
    cilindro: () => cilindro(),
    estrutura: () => estrutura(3),
    reator: reator,
    capacete: capacete,
    manopla: () => cilindro(0.55, 1.5, 16, 7),
  };

  const NOMES = {
    reator: "REATOR ARC", capacete: "CAPACETE", manopla: "MANOPLA",
    esfera: "NÚCLEO", toroide: "ANEL DE ENERGIA", cilindro: "MOTOR", estrutura: "ESTRUTURA",
  };

  let mesh = null, cor = "#35e6ff", ang = 0, tilt = 0.5, running = false;

  function projeta(p, cx, cy, zoom) {
    // rotação Y (ang) e X (tilt)
    let [x, y, z] = p;
    let x1 = x * Math.cos(ang) - z * Math.sin(ang);
    let z1 = x * Math.sin(ang) + z * Math.cos(ang);
    let y1 = y * Math.cos(tilt) - z1 * Math.sin(tilt);
    let z2 = y * Math.sin(tilt) + z1 * Math.cos(tilt);
    const fov = 4, scale = (fov / (fov + z2)) * zoom;
    return [cx + x1 * scale, cy - y1 * scale, z2];
  }

  function frame() {
    if (!running || !mesh) return;
    const w = canvas.width, h = canvas.height, cx = w / 2, cy = h / 2, zoom = w * 0.32;
    ctx.clearRect(0, 0, w, h);
    ang += 0.012;

    // arestas
    ctx.lineWidth = 1.3;
    for (const [a, b] of mesh.e) {
      const pa = projeta(mesh.v[a], cx, cy, zoom);
      const pb = projeta(mesh.v[b], cx, cy, zoom);
      const depth = (pa[2] + pb[2]) / 2;
      ctx.globalAlpha = Math.min(1, Math.max(0.15, 0.75 + depth * 0.12));
      ctx.strokeStyle = cor;
      ctx.shadowColor = cor;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.moveTo(pa[0], pa[1]);
      ctx.lineTo(pb[0], pb[1]);
      ctx.stroke();
    }
    // vértices
    ctx.shadowBlur = 6;
    for (const p of mesh.v) {
      const pp = projeta(p, cx, cy, zoom);
      ctx.globalAlpha = 0.9;
      ctx.fillStyle = "#eafcff";
      ctx.beginPath();
      ctx.arc(pp[0], pp[1], 1.6, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
    requestAnimationFrame(frame);
  }

  function show(forma, peca, corHex) {
    const f = BUILDERS[forma] ? forma : "reator";
    mesh = BUILDERS[f]();
    cor = corHex || "#35e6ff";
    title.textContent = (peca && peca.toUpperCase()) || NOMES[f] || f.toUpperCase();
    panel.classList.remove("hidden");
    if (!running) { running = true; frame(); }
  }

  function hide() {
    running = false;
    panel.classList.add("hidden");
  }

  // API global para o app.js
  window.HoloLab = { show, hide };

  // controlos
  document.getElementById("holoClose").addEventListener("click", hide);
  const sel = document.getElementById("holoSelect");
  if (sel) sel.addEventListener("change", () => show(sel.value, null, cor));
})();
