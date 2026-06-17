import { escapeHtml } from "./lib/format.js";

const ctx = window.FS_CONTEXT || {};
const V = ctx.assetVersion || "";
const withV = (p) => p + "?v=" + V;

const VIEW_MODULES = {
  "": "./views/home.js",
  "entry": "./views/entry.js",
  "trace": "./views/trace.js",
  "dashboard": "./views/dashboard.js",
};

const NAV = [
  { route: "", label: "Hôm nay", icon: "today" },
  { route: "trace", label: "Truy xuất lô", icon: "search" },
];

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
  const nav = NAV.slice();
  if (ctx.isManager) nav.push({ route: "dashboard", label: "Bảng điều khiển", icon: "dashboard" });
  root.innerHTML = `
    <header class="app-header">
      <div class="app-brand">${sym("security")}<span>ATTP Hoàng Giang</span></div>
      <span class="app-user">${sym("account_circle")}${escapeHtml(ctx.user || "")}</span>
    </header>
    <main id="app-main" class="app-main"></main>
    <nav class="app-bottomnav">${nav.map((n) =>
      `<a class="app-tab" data-route="${n.route}" href="#/${n.route}">
        <span class="app-tab-ic">${sym(n.icon)}</span><span>${escapeHtml(n.label)}</span></a>`).join("")}</nav>`;
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
window.addEventListener("hashchange", route);
route();
