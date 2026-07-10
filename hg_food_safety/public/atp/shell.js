import { escapeHtml } from "./lib/format.js";

const ctx = window.FS_CONTEXT || {};
const V = ctx.assetVersion || "";
const withV = (p) => p + "?v=" + V;

const VIEW_MODULES = {
  "": "./views/home.js",
  "entry": "./views/entry.js",
  "trace": "./views/trace.js",
  "documents": "./views/documents.js",
  "dashboard": "./views/dashboard.js",
};

const NAV = [
  { route: "", label: "Hôm nay", icon: "today" },
  { route: "trace", label: "Truy xuất", icon: "search" },
  { route: "documents", label: "Tài liệu", icon: "folder_open" },
];

const SEASONS = [
  { key: "spring", emoji: "🌸", label: "Xuân" },
  { key: "summer", emoji: "☀️", label: "Hạ" },
  { key: "autumn", emoji: "🍂", label: "Thu" },
  { key: "winter", emoji: "❄️", label: "Đông" },
];
const SEASON_KEYS = SEASONS.map((s) => s.key);

function detectSeason() {
  const m = new Date().getMonth() + 1;
  if (m >= 2 && m <= 4) return "spring";
  if (m >= 5 && m <= 7) return "summer";
  if (m >= 8 && m <= 10) return "autumn";
  return "winter";
}
function currentSeason() {
  try { return localStorage.getItem("attp_season") || detectSeason(); }
  catch (e) { return detectSeason(); }
}
function applySeason(key) {
  const root = document.getElementById("app-root");
  SEASON_KEYS.forEach((k) => root.classList.remove("app-" + k));
  root.classList.add("app-" + key);
  const btn = document.getElementById("app-season-btn");
  if (btn) btn.querySelector(".app-emoji").textContent = (SEASONS.find((s) => s.key === key) || SEASONS[0]).emoji;
}

function parseHash() {
  const h = (location.hash || "#/").replace(/^#\/?/, "");
  const [path, qs] = h.split("?");
  const query = {};
  new URLSearchParams(qs || "").forEach((v, k) => (query[k] = v));
  return { route: path || "", query };
}

function sym(name) { return `<span class="material-symbols-outlined">${name}</span>`; }

function renderShell() {
  const root = document.getElementById("app-root");
  const roleLabel = ctx.isManager ? "QA" : "KCS";
  const nav = [
    { route: "", label: "Hôm nay", icon: "today" },
    { route: "trace", label: "Truy xuất", icon: "search" },
    { route: "documents", label: ctx.isManager ? "Tài liệu" : "Hồ sơ", icon: "folder_open" },
  ];
  if (ctx.isManager) nav.push({ route: "dashboard", label: "Bảng ĐK", icon: "dashboard" });
  const season = SEASONS.find((s) => s.key === currentSeason()) || SEASONS[0];
  root.innerHTML = `
    <header class="app-header">
      <div class="app-header-inner">
        <a class="app-brand" href="#/">
          <span class="app-brand-badge">${sym("health_and_safety")}</span>
          <span class="app-brand-txt">
            <span class="app-brand-name">ATTP Hoàng Giang</span>
            <span class="app-brand-sub">An toàn thực phẩm · ISO 22000</span>
          </span>
        </a>
        <div class="app-header-actions">
          <span class="app-role-chip app-role-${roleLabel === "QA" ? "qa" : "qc"}">${roleLabel}</span>
          <button class="app-icon-btn" id="app-refresh" aria-label="Làm mới" title="Làm mới">${sym("refresh")}</button>
          <button class="app-icon-btn" id="app-season-btn" aria-label="Đổi mùa" title="Đổi mùa giao diện"><span class="app-emoji">${season.emoji}</span></button>
          <button class="app-icon-btn" id="app-acct-btn" aria-label="Tài khoản" title="Tài khoản">${sym("account_circle")}</button>
        </div>
      </div>
    </header>
    <main id="app-main" class="app-main"></main>
    <nav class="app-bottomnav">${nav.map((n) =>
      `<a class="app-tab" data-route="${n.route}" href="#/${n.route}">
        <span class="app-tab-ic">${sym(n.icon)}</span><span>${escapeHtml(n.label)}</span></a>`).join("")}</nav>
    <div id="app-acct-menu" class="app-acct-menu" hidden>
      <div class="app-acct-name">${escapeHtml(ctx.user || "")}</div>
      <div class="app-acct-sub">${ctx.isManager ? "Quản lý ATTP (QA)" : "Nhân viên KCS"}</div>
      <button class="app-acct-logout" id="app-logout">Đăng xuất</button>
    </div>`;

  document.getElementById("app-refresh").addEventListener("click", route);
  document.getElementById("app-season-btn").addEventListener("click", openSeasonPicker);
  const acctBtn = document.getElementById("app-acct-btn");
  const acctMenu = document.getElementById("app-acct-menu");
  acctBtn.addEventListener("click", (e) => { e.stopPropagation(); acctMenu.hidden = !acctMenu.hidden; });
  document.addEventListener("click", (e) => {
    if (!acctMenu.hidden && !acctMenu.contains(e.target) && e.target !== acctBtn) acctMenu.hidden = true;
  });
  document.getElementById("app-logout").addEventListener("click", logout);
}

function openSeasonPicker() {
  const cur = currentSeason();
  const host = document.querySelector(".app-root") || document.body;
  const ov = document.createElement("div");
  ov.className = "app-modal-ov";
  ov.innerHTML = `<div class="app-modal" role="dialog" aria-modal="true">
    <div class="app-modal-head"><span>Giao diện theo mùa</span><button class="app-modal-x" aria-label="Đóng">×</button></div>
    <div class="app-modal-body">
      <div class="app-season-grid">${SEASONS.map((s) =>
        `<button class="app-season-opt ${s.key === cur ? "app-active" : ""}" data-season="${s.key}">
          <span class="app-emoji">${s.emoji}</span><span>${s.label}</span></button>`).join("")}</div>
    </div></div>`;
  host.appendChild(ov);
  const close = () => ov.remove();
  ov.addEventListener("click", (e) => { if (e.target === ov) close(); });
  ov.querySelector(".app-modal-x").addEventListener("click", close);
  ov.querySelectorAll("[data-season]").forEach((b) =>
    b.addEventListener("click", () => {
      const k = b.dataset.season;
      try { localStorage.setItem("attp_season", k); } catch (e) {}
      applySeason(k);
      close();
    }));
}

async function logout() {
  try {
    await fetch("/api/method/logout", { method: "POST", headers: { "X-Frappe-CSRF-Token": ctx.csrf || "" } });
  } catch (e) {}
  window.location.href = "/login";
}

async function route() {
  const { route, query } = parseHash();
  const main = document.getElementById("app-main");
  const key = VIEW_MODULES[route] ? route : "";
  const mod = VIEW_MODULES[key];
  document.querySelectorAll(".app-tab").forEach((a) =>
    a.classList.toggle("app-active", a.getAttribute("data-route") === route));
  main.innerHTML = '<div class="app-card app-muted">Đang tải...</div>';
  try {
    const m = await import(withV(mod));
    await m.render({ container: main, query, params: {} });
    window.scrollTo(0, 0);
  } catch (e) {
    main.innerHTML = `<div class="app-alert app-alert-red">Lỗi tải màn hình: ${escapeHtml(e.message)}</div>`;
  }
}

renderShell();
applySeason(currentSeason());
window.addEventListener("hashchange", route);
route();
