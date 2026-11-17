(function () {
  "use strict";

  var WA_NUMBER = "905321205338";

  // Mobil menü
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Menüyü kapat" : "Menüyü aç");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Menüyü aç");
        toggle.focus();
      }
    });
  }

  // Teklif formu: bilgileri WhatsApp mesajına çevirir
  var forms = document.querySelectorAll("form[data-quote]");
  Array.prototype.forEach.call(forms, function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var get = function (name) {
        var el = form.elements[name];
        return el ? String(el.value || "").trim() : "";
      };
      var service = get("hizmet");
      var district = get("ilce");
      var name = get("ad");
      var note = get("not");
      var error = form.querySelector(".form-error");

      if (!service || !district) {
        if (error) error.textContent = "Teklif için hizmet türünü ve ilçeyi seçin.";
        (service ? form.elements["ilce"] : form.elements["hizmet"]).focus();
        return;
      }
      if (error) error.textContent = "";

      var lines = ["Merhaba, temizlik hizmeti için teklif almak istiyorum."];
      lines.push("Hizmet: " + service);
      lines.push("İlçe: " + district);
      if (note) lines.push("Detay: " + note);
      if (name) lines.push("Adım: " + name);

      var url = "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(lines.join("\n"));
      window.open(url, "_blank", "noopener");
    });
  });

  // Hizmet sayfasından gelen ön seçim (?hizmet=...)
  try {
    var params = new URLSearchParams(window.location.search);
    var pre = params.get("hizmet");
    if (pre) {
      Array.prototype.forEach.call(forms, function (form) {
        var sel = form.elements["hizmet"];
        if (sel) sel.value = pre;
      });
    }
  } catch (err) { /* eski tarayıcılarda sessizce geç */ }

  // Telif yılı
  var year = document.querySelectorAll("[data-year]");
  Array.prototype.forEach.call(year, function (el) { el.textContent = new Date().getFullYear(); });
})();
