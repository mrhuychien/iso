import { escapeHtml } from "./lib/format.js";

const ctx = window.FS_CONTEXT || {};
const V = ctx.assetVersion || "";
const withV = (p) => p + "?v=" + V;

const VIEW_MODULES = {
  "": "./views/home.js",
  "trace": "./views/trace.js",
  "dashboard": "./views/dashboard.js",
};

function parseHash() {
  const h = (location.hash || "#/").replace(/^#\/?/, "");
  const [path, qs] = h.split("?");
  const query = {};
  new URLSearchParams(qs || "").forEach((v, k) => (query[k] = v));
  return { route: path || "", query };
}

function renderShell() {
  const root = document.getElementById("app-root");
  const nav = [
    { route: "", label: "Hom nay" },
    { route: "trace", label: "Truy xuat lo" },
  ];
  if (ctx.isManager) nav.push({ route: "dashboard", label: "Dashboard" });
  root.innerHTML = `
    <header class="app-header">
      <span class="app-brand">ATTP Hoang Giang</span>
      <span class="app-user">${escapeHtml(ctx.user || "")}</span>
    </header>
    <nav class="app-nav">${nav.map((n) =>
      `<a class="app-nav-link" href="#/${n.route}">${escapeHtml(n.label)}</a>`).join("")}</nav>
    <main id="app-main" class="app-main"></main>`;
}

async function route() {
  const { route, query, params } = { ...parseHash() };
  const main = document.getElementById("app-main");
  const mod = VIEW_MODULES[route] || VIEW_MODULES[""];
  document.querySelectorAll(".app-nav-link").forEach((a) =>
    a.classList.toggle("app-active", a.getAttribute("href") === "#/" + route));
  main.innerHTML = '<div class="app-card">Dang tai...</div>';
  try {
    const m = await import(withV(mod));
    await m.render({ container: main, query, params: {} });
  } catch (e) {
    main.innerHTML = `<div class="app-alert app-alert-red">Loi tai view: ${escapeHtml(e.message)}</div>`;
  }
}

renderShell();
window.addEventListener("hashchange", route);
route();
