const menuToggle = document.querySelector(".menu-toggle");
const primaryNav = document.querySelector(".primary-nav");

const closeMenu = () => {
  if (!menuToggle || !primaryNav) return;
  menuToggle.setAttribute("aria-expanded", "false");
  menuToggle.setAttribute("aria-label", "Menüyü aç");
  primaryNav.classList.remove("is-open");
};

if (menuToggle && primaryNav) {
  menuToggle.addEventListener("click", () => {
    const isExpanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isExpanded));
    menuToggle.setAttribute("aria-label", isExpanded ? "Menüyü aç" : "Menüyü kapat");
    primaryNav.classList.toggle("is-open", !isExpanded);
  });

  primaryNav.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.closest("a")) {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (menuToggle.getAttribute("aria-expanded") !== "true") return;
    if (event.target instanceof Node && !primaryNav.contains(event.target) && !menuToggle.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
}

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());

const revealTargets = document.querySelectorAll(".reveal-target");
const initScrollReveals = () => {
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  document.body.classList.add("reveal-ready");
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
      } else {
        entry.target.classList.remove("is-visible");
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -24px 0px" });

  revealTargets.forEach((element, index) => {
    element.dataset.reveal = "";
    element.style.setProperty("--reveal-delay", `${(index % 5) * 70}ms`);
    revealObserver.observe(element);
  });
};

if (document.visibilityState === "visible") {
  initScrollReveals();
} else {
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      initScrollReveals();
    }
  }, { once: true });
}
