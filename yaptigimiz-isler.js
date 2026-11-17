const apiUrl = "portfolio-api.php";
const workGrid = document.querySelector("#work-grid");
const workStatus = document.querySelector("#work-status");
const workEmpty = document.querySelector("#work-empty");
const workFilters = document.querySelector("#work-filters");
const adminDialog = document.querySelector("#admin-dialog");
const adminMessage = document.querySelector("#admin-message");
const adminLoginForm = document.querySelector("#admin-login-form");
const adminContent = document.querySelector("#admin-content");
const uploadForm = document.querySelector("#work-upload-form");
const uploadInput = document.querySelector("#work-media");
const uploadPreview = document.querySelector("#upload-preview");
let currentCsrfToken = "";
let works = [];
let selectedCategory = "Tümü";
let isAdmin = false;
let workLoadError = "";

const request = async (url, options = {}) => {
  const response = await fetch(url, { credentials: "same-origin", ...options });
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Sunucudan geçerli bir yanıt alınamadı.");
  }
  if (!response.ok || !payload || payload.ok !== true) {
    throw new Error(payload?.error || "İşlem tamamlanamadı.");
  }
  return payload;
};

const animateCount = (element, end) => {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    element.textContent = String(end);
    return;
  }
  const duration = 850;
  const startTime = performance.now();
  const step = (now) => {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - (1 - progress) ** 3;
    element.textContent = String(Math.round(end * eased));
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
};

const updateStats = () => {
  const media = works.flatMap((work) => work.media);
  const counts = {
    works: works.length,
    photos: media.filter((item) => item.type === "image").length,
    videos: media.filter((item) => item.type === "video").length,
  };
  document.querySelectorAll("[data-stat]").forEach((element) => {
    animateCount(element, counts[element.dataset.stat] ?? 0);
  });
};

const makeMedia = (item, title) => {
  const figure = document.createElement("figure");
  figure.className = "work-media-item";
  if (item.type === "video") {
    const video = document.createElement("video");
    video.controls = true;
    video.preload = "metadata";
    video.playsInline = true;
    video.src = item.url;
    video.setAttribute("aria-label", `${title} çalışmasından video`);
    figure.append(video);
  } else {
    const image = document.createElement("img");
    image.src = item.url;
    image.alt = `${title} çalışmasından fotoğraf`;
    image.loading = "lazy";
    image.decoding = "async";
    figure.append(image);
  }
  return figure;
};

const makeWorkCard = (work) => {
  const card = document.createElement("article");
  card.className = "work-card";
  const media = document.createElement("div");
  media.className = "work-card-media";
  work.media.forEach((item) => media.append(makeMedia(item, work.title)));

  const copy = document.createElement("div");
  copy.className = "work-card-copy";
  const category = document.createElement("span");
  category.className = "portfolio-category";
  category.textContent = work.category;
  const title = document.createElement("h3");
  title.textContent = work.title;
  const description = document.createElement("p");
  description.textContent = work.description;
  const date = document.createElement("time");
  date.className = "work-date";
  date.dateTime = work.createdAt;
  date.textContent = new Intl.DateTimeFormat("tr-TR", { year: "numeric", month: "long" }).format(new Date(work.createdAt));
  copy.append(category, title, description, date);

  if (isAdmin) {
    const remove = document.createElement("button");
    remove.className = "work-delete";
    remove.type = "button";
    remove.textContent = "Bu işi kaldır";
    remove.addEventListener("click", () => deleteWork(work.id, remove));
    copy.append(remove);
  }
  card.append(media, copy);
  return card;
};

const renderFilters = () => {
  const categories = ["Tümü", ...new Set(works.map((work) => work.category))];
  if (!categories.includes(selectedCategory)) selectedCategory = "Tümü";
  workFilters.replaceChildren();
  categories.forEach((category) => {
    const button = document.createElement("button");
    button.className = "work-filter";
    button.type = "button";
    button.textContent = category;
    button.setAttribute("aria-pressed", String(category === selectedCategory));
    button.addEventListener("click", () => {
      selectedCategory = category;
      renderWorks();
    });
    workFilters.append(button);
  });
};

const renderWorks = () => {
  renderFilters();
  const visibleWorks = selectedCategory === "Tümü"
    ? works
    : works.filter((work) => work.category === selectedCategory);
  workGrid.replaceChildren(...visibleWorks.map(makeWorkCard));
  workEmpty.hidden = works.length > 0 || Boolean(workLoadError);
  workStatus.textContent = workLoadError
    ? `Çalışmalar yüklenemedi: ${workLoadError}`
    : works.length
      ? `${visibleWorks.length} çalışma gösteriliyor.`
      : "Henüz yayınlanmış çalışma yok.";
  workStatus.classList.toggle("is-error", Boolean(workLoadError));
  updateStats();
};

const setAdminState = (loggedIn, token = "") => {
  isAdmin = loggedIn;
  currentCsrfToken = token;
  adminLoginForm.hidden = loggedIn;
  adminContent.hidden = !loggedIn;
  if (!workLoadError || works.length > 0) renderWorks();
};

const loadSession = async () => {
  const payload = await request(`${apiUrl}?action=session`);
  setAdminState(payload.authenticated, payload.csrfToken || "");
};

const loadWorks = async () => {
  try {
    const payload = await request(`${apiUrl}?action=works`);
    if (!Array.isArray(payload.works)) {
      throw new Error("Sunucu geçerli bir iş listesi döndürmedi.");
    }
    workLoadError = "";
    works = payload.works;
    renderWorks();
  } catch (error) {
    workLoadError = error.message;
    renderWorks();
  }
};

const showAdminMessage = (message, isError = false) => {
  adminMessage.textContent = message;
  adminMessage.classList.toggle("is-error", isError);
};

const deleteWork = async (id, button) => {
  if (!window.confirm("Bu çalışmayı ve yüklenen medya dosyalarını kaldırmak istiyor musunuz?")) return;
  button.disabled = true;
  try {
    const payload = await request(`${apiUrl}?action=delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, csrfToken: currentCsrfToken }),
    });
    currentCsrfToken = payload.csrfToken;
    works = works.filter((work) => work.id !== id);
    renderWorks();
    showAdminMessage("Çalışma kaldırıldı.");
  } catch (error) {
    button.disabled = false;
    showAdminMessage(error.message, true);
  }
};

document.querySelector("#open-admin").addEventListener("click", async () => {
  adminDialog.showModal();
  showAdminMessage("");
  try {
    await loadSession();
  } catch (error) {
    showAdminMessage(error.message, true);
  }
});

document.querySelector("#close-admin").addEventListener("click", () => adminDialog.close());
adminDialog.addEventListener("click", (event) => {
  if (event.target === adminDialog) adminDialog.close();
});

adminLoginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = adminLoginForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  try {
    const payload = await request(`${apiUrl}?action=login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password: new FormData(adminLoginForm).get("password"),
        csrfToken: currentCsrfToken,
      }),
    });
    adminLoginForm.reset();
    setAdminState(true, payload.csrfToken);
    showAdminMessage("Giriş başarılı. Yeni çalışma ekleyebilirsiniz.");
  } catch (error) {
    showAdminMessage(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

document.querySelector("#admin-logout").addEventListener("click", async () => {
  try {
    await request(`${apiUrl}?action=logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ csrfToken: currentCsrfToken }),
    });
    setAdminState(false);
    showAdminMessage("Oturum kapatıldı.");
  } catch (error) {
    showAdminMessage(error.message, true);
  }
});

uploadInput.addEventListener("change", () => {
  uploadPreview.replaceChildren();
  [...uploadInput.files].forEach((file) => {
    const item = document.createElement("span");
    item.textContent = `${file.name} · ${(file.size / (1024 * 1024)).toFixed(1)} MB`;
    uploadPreview.append(item);
  });
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const files = [...uploadInput.files];
  if (files.length > 8 || files.some((file) => file.size > 20 * 1024 * 1024)) {
    showAdminMessage("En fazla 8 dosya, dosya başına 20 MB yükleyebilirsiniz.", true);
    return;
  }
  if (files.reduce((total, file) => total + file.size, 0) > 110 * 1024 * 1024) {
    showAdminMessage("Bir çalışma için toplam dosya boyutu 110 MB'ı aşamaz.", true);
    return;
  }
  const submitButton = uploadForm.querySelector('button[type="submit"]');
  const formData = new FormData(uploadForm);
  formData.append("csrfToken", currentCsrfToken);
  submitButton.disabled = true;
  showAdminMessage("Medya yükleniyor, lütfen bekleyin.");
  try {
    const payload = await request(`${apiUrl}?action=create`, { method: "POST", body: formData });
    currentCsrfToken = payload.csrfToken;
    works = payload.works;
    uploadForm.reset();
    uploadPreview.replaceChildren();
    renderWorks();
    showAdminMessage("Çalışma yayınlandı ve galeride görüntülenebilir.");
  } catch (error) {
    showAdminMessage(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

const loadPage = async () => {
  await Promise.all([loadWorks(), loadSession().catch(() => {})]);
};

loadPage();
