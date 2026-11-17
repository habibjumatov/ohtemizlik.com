(function () {
  "use strict";

  var WA_NUMBER = "905321205338";
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };

  /* Mobil menü */
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Menüyü kapat" : "Menüyü aç");
    };
    toggle.addEventListener("click", function () { setOpen(!nav.classList.contains("is-open")); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
  }

  /* Teklif formu: seçimleri WhatsApp mesajına çevirir */
  var forms = document.querySelectorAll("form[data-quote]");
  each(forms, function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var val = function (n) { var el = form.elements[n]; return el ? String(el.value || "").trim() : ""; };
      var service = val("hizmet"), district = val("ilce"), name = val("ad"), note = val("not");
      var error = form.querySelector(".form-error");
      if (!service || !district) {
        if (error) error.textContent = "Teklif için hizmet türünü ve ilçeyi seçin.";
        (service ? form.elements.ilce : form.elements.hizmet).focus();
        return;
      }
      if (error) error.textContent = "";
      var lines = ["Merhaba, temizlik hizmeti için teklif almak istiyorum.", "Hizmet: " + service, "İlçe: " + district];
      if (note) lines.push("Detay: " + note);
      if (name) lines.push("Adım: " + name);
      window.location.href = "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(lines.join("\n"));
    });
  });

  /* Telif yılı */
  each(document.querySelectorAll("[data-year]"), function (el) { el.textContent = new Date().getFullYear(); });

  /* Buğulu cam: başlık buğunun ardında, silecek bir kez geçer, gerisini ziyaretçi siler */
  var glass = document.querySelector("[data-glass]");
  if (!glass) return;
  var hero = glass.closest(".hero");
  var hint = document.querySelector(".glass-hint");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canvas = document.createElement("canvas");
  if (reduce || !canvas.getContext) { if (hero) hero.classList.add("no-fog"); return; }

  canvas.className = "fog";
  canvas.setAttribute("aria-hidden", "true");
  glass.appendChild(canvas);
  var ctx = canvas.getContext("2d");
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, lastW = -1, touched = false, animating = false;

  function rand(a, b) { return a + Math.random() * (b - a); }

  function paintFog() {
    ctx.globalCompositeOperation = "source-over";
    ctx.shadowBlur = 0;
    ctx.clearRect(0, 0, W, H);
    var g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "rgba(222, 226, 255, 0.95)");
    g.addColorStop(1, "rgba(196, 203, 255, 0.92)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    var n = Math.round((W * H) / 260);
    for (var i = 0; i < n; i++) {
      var big = Math.random() > 0.94;
      var r = big ? rand(2.2, 5.5) : rand(0.4, 1.7);
      var x = rand(0, W), y = rand(0, H);
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255, 255, 255, " + rand(0.35, 0.85).toFixed(2) + ")";
      ctx.fill();
      if (big) {
        ctx.strokeStyle = "rgba(20, 28, 158, 0.22)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }

  function wipe(x1, y1, x2, y2, w) {
    ctx.globalCompositeOperation = "destination-out";
    ctx.shadowColor = "rgba(0, 0, 0, 1)";
    ctx.shadowBlur = 14;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineWidth = w;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  // Silecek yolu: satır satır, hafif eğimli geçişler
  function squeegeePath() {
    var rows = Math.max(1, Math.round(H / 140));
    var band = H / rows;
    var pts = [];
    for (var r = 0; r < rows; r++) {
      var y = band * (r + 0.5);
      var ltr = r % 2 === 0;
      pts.push([ltr ? -40 : W + 40, y - band * 0.08]);
      pts.push([ltr ? W + 40 : -40, y + band * 0.08]);
    }
    return { pts: pts, width: band * 0.92 };
  }

  function runSqueegee(instant) {
    var p = squeegeePath();
    var segs = [], total = 0;
    for (var i = 1; i < p.pts.length; i++) {
      var a = p.pts[i - 1], b = p.pts[i];
      var len = Math.hypot(b[0] - a[0], b[1] - a[1]);
      segs.push({ a: a, b: b, len: len });
      total += len;
    }
    if (instant) {
      segs.forEach(function (s) { wipe(s.a[0], s.a[1], s.b[0], s.b[1], p.width); });
      return;
    }
    animating = true;
    var duration = 650 * segs.length + 400;
    var start = null, done = 0;
    function point(d) {
      var acc = 0;
      for (var k = 0; k < segs.length; k++) {
        if (acc + segs[k].len >= d) {
          var t = (d - acc) / segs[k].len, s = segs[k];
          return [s.a[0] + (s.b[0] - s.a[0]) * t, s.a[1] + (s.b[1] - s.a[1]) * t];
        }
        acc += segs[k].len;
      }
      var last = segs[segs.length - 1].b;
      return [last[0], last[1]];
    }
    function frame(ts) {
      if (start === null) start = ts;
      var t = Math.min(1, (ts - start) / duration);
      var eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      var target = eased * total;
      var step = 6;
      for (var d = done; d < target; d += step) {
        var p1 = point(d), p2 = point(Math.min(target, d + step));
        wipe(p1[0], p1[1], p2[0], p2[1], p.width);
      }
      done = target;
      if (t < 1) requestAnimationFrame(frame);
      else animating = false;
    }
    requestAnimationFrame(frame);
  }

  function setup(first) {
    var r = glass.getBoundingClientRect();
    var c = canvas.getBoundingClientRect();
    W = c.width; H = c.height;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lastW = r.width;
    paintFog();
    if (first) setTimeout(function () { runSqueegee(false); }, 450);
    else runSqueegee(true);
  }

  // Ziyaretçinin silmesi
  var last = null;
  function local(x, y) { var c = canvas.getBoundingClientRect(); return [x - c.left, y - c.top]; }
  function wipeAt(x, y) {
    var p = local(x, y);
    var w = Math.max(48, Math.min(110, H * 0.28));
    if (last) wipe(last[0], last[1], p[0], p[1], w);
    else wipe(p[0] - 0.1, p[1], p[0], p[1], w);
    last = p;
    if (!touched && !animating) {
      touched = true;
      if (hint) hint.classList.add("is-done");
    }
  }
  glass.addEventListener("pointermove", function (e) {
    if (e.pointerType === "mouse") wipeAt(e.clientX, e.clientY);
  });
  glass.addEventListener("pointerleave", function () { last = null; });
  glass.addEventListener("touchstart", function (e) { last = null; wipeAt(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
  glass.addEventListener("touchmove", function (e) { wipeAt(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
  glass.addEventListener("touchend", function () { last = null; }, { passive: true });

  var start = function () { setup(true); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(start); else window.addEventListener("load", start);

  var rt;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () {
      if (Math.abs(glass.getBoundingClientRect().width - lastW) > 2) setup(false);
    }, 150);
  });
})();
