// Background constellations: faint stars, joined by thin lines, fade in around the
// mouse cursor. Pure decoration; the site works without this file.
(function () {
  // Mouse-and-hover devices only; respect reduced motion.
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var root = document.documentElement;
  var canvas = document.createElement("canvas");
  canvas.setAttribute("aria-hidden", "true");
  canvas.style.cssText = "position:fixed;inset:0;width:100%;height:100%;z-index:-1;pointer-events:none";
  document.body.prepend(canvas);
  var ctx = canvas.getContext("2d");

  var R = 270;          // reveal radius (px)
  var LINK = 115;       // max length of a constellation line (px)
  var W = 0, H = 0;
  var mouse = { x: 0, y: 0, sx: 0, sy: 0, inside: false, seen: false };
  var stars = [], running = false, dark = true, color = "";

  function readTheme() {
    var t = root.dataset.theme;
    dark = t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    color = dark ? "205,222,255" : "11,70,130";
    kick();
  }

  function rand(a, b) { return a + Math.random() * (b - a); }

  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    stars = [];
    var n = Math.round(W * H / 2600);
    for (var i = 0; i < n; i++) {
      stars.push({ x: rand(0, W), y: rand(0, H), r: Math.random() < 0.9 ? rand(0.4, 1.1) : rand(1.2, 1.8),
                   b: rand(0.5, 1), tw: rand(0, 6.28), ts: rand(0.8, 2.2) });
    }
    kick();
  }

  function frame(t) {
    mouse.sx += (mouse.x - mouse.sx) * 0.2;
    mouse.sy += (mouse.y - mouse.sy) * 0.2;
    ctx.clearRect(0, 0, W, H);
    if (!mouse.inside) { running = false; return; }

    var peak = dark ? 0.75 : 0.45, lineA = dark ? 0.4 : 0.26;
    var shift = window.scrollY * 0.25, near = [];
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var y = (s.y - shift) % H; if (y < 0) y += H; // slight parallax, wrapped
      var dx = s.x - mouse.sx, dy = y - mouse.sy;
      var k = 1 - Math.sqrt(dx * dx + dy * dy) / R;
      if (k <= 0) continue;
      var f = k * k;
      var a = f * s.b * (0.75 + 0.25 * Math.sin(t * 0.001 * s.ts + s.tw)) * peak;
      ctx.fillStyle = "rgba(" + color + "," + a.toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(s.x, y, s.r, 0, 6.2832); ctx.fill();
      near.push({ x: s.x, y: y, f: f });
    }

    ctx.lineWidth = 0.7;
    for (var p = 0; p < near.length; p++) {
      for (var q = p + 1, links = 0; q < near.length && links < 3; q++) {
        var ex = near[p].x - near[q].x, ey = near[p].y - near[q].y;
        var d = Math.sqrt(ex * ex + ey * ey);
        if (d > LINK) continue;
        links++;
        var al = (1 - d / LINK) * Math.min(near[p].f, near[q].f) * lineA;
        ctx.strokeStyle = "rgba(" + color + "," + al.toFixed(3) + ")";
        ctx.beginPath(); ctx.moveTo(near[p].x, near[p].y); ctx.lineTo(near[q].x, near[q].y); ctx.stroke();
      }
    }

    if (mouse.inside) requestAnimationFrame(frame); // keep twinkling while on the page
    else running = false;
  }

  function kick() {
    if (running || !mouse.seen) return;
    running = true;
    requestAnimationFrame(frame);
  }

  window.addEventListener("pointermove", function (ev) {
    if (ev.pointerType !== "mouse") return;
    mouse.x = ev.clientX; mouse.y = ev.clientY;
    if (!mouse.seen) { mouse.sx = mouse.x; mouse.sy = mouse.y; mouse.seen = true; }
    mouse.inside = true;
    kick();
  }, { passive: true });
  document.addEventListener("mouseleave", function () {
    mouse.inside = false;
    ctx.clearRect(0, 0, W, H);
  });
  window.addEventListener("resize", resize);
  new MutationObserver(readTheme).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", readTheme);

  resize();
  readTheme();
})();
