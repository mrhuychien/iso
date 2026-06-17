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
  { route: "", label: "Hôm nay", icon: "M3 12l9-9 9 9M5 10v10h14V10" },
  { route: "trace", label: "Truy xuất lô", icon: "M21 21l-5-5M3 10a7 7 0 1014 0 7 7 0 00-14 0" },
];

function parseHash() {
  const h = (location.hash || "#/").replace(/^#\/?/, "");
  const [path, qs] = h.split("?");
  const query = {};
  new URLSearchParams(qs || "").forEach((v, k) => (query[k] = v));
  return { route: path || "", query };
}

function renderShell() {
  const root = document.getElementById("app-root");
  const nav = NAV.slice();
  if (ctx.isManager) nav.push({ route: "dashboard", label: "Bảng điều khiển", icon: "M4 13h6V4H4zM14 21h6v-9h-6zM14 4v5h6V4zM4 21h6v-5H4z" });
  root.innerHTML = `
    <header class="app-header">
      <div class="app-brand"><span class="app-logo">ATTP</span><span>Hoàng Giang</span></div>
      <span class="app-user">${escapeHtml(ctx.user || "")}</span>
    </header>
    <main id="app-main" class="app-main"></main>
    <nav class="app-bottomnav">${nav.map((n) =>
      `<a class="app-tab" data-route="${n.route}" href="#/${n.route}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${n.icon}"/></svg>
        <span>${escapeHtml(n.label)}</span></a>`).join("")}</nav>`;
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
