import { call } from "../lib/api.js";
import { escapeHtml } from "../lib/format.js";

export async function render({ container, query }) {
  const batch = query.batch || "";
  container.innerHTML = `
    <h2 class="app-h2">Truy xuat theo lo</h2>
    <div class="app-row">
      <input id="app-batch" class="app-input" placeholder="Nhap ma lo (Batch)" value="${escapeHtml(batch)}">
      <button id="app-go" class="app-btn">Truy xuat</button>
    </div>
    <div id="app-trace-result"></div>`;
  const go = () => {
    const b = document.getElementById("app-batch").value.trim();
    if (b) { location.hash = "#/trace?batch=" + encodeURIComponent(b); }
  };
  container.querySelector("#app-go").addEventListener("click", go);
  if (batch) await load(batch, container.querySelector("#app-trace-result"));
}

async function load(batch, target) {
  target.innerHTML = "Dang tai...";
  try {
    const d = await call("hg_food_safety.api.trace.by_batch", { batch_no: batch });
    const sec = (title, rows, fmt) => `
      <div class="app-tl-sec"><div class="app-tl-title">${escapeHtml(title)} (${(rows || []).length})</div>
      ${(rows || []).map(fmt).join("") || '<div class="app-tl-empty">- khong co -</div>'}</div>`;
    target.innerHTML = `
      <div class="app-alert">Trang thai lo: <b>${escapeHtml(d.batch_status || "-")}</b></div>
      ${sec("Giam sat OPRP", d.oprp, (r) => line(r.name, r.log_date + " / " + r.shift + (r.has_deviation ? " - VUOT" : "")))}
      ${sec("Kiem di vat", d.foreign_body, (r) => line(r.name, r.log_date + " - " + r.status))}
      ${sec("Kiem thanh pham", d.finished_inspection, (r) => line(r.name, (r.item_code || "") + " - " + r.status))}
      ${sec("Luu mau", d.sample_retention, (r) => line(r.name, r.retention_date + " -> " + (r.keep_until || "")))}`;
  } catch (e) {
    target.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`;
  }
}

function line(name, detail) {
  return `<div class="app-tl-row"><span class="app-tl-name">${escapeHtml(name)}</span>
    <span class="app-tl-detail">${escapeHtml(detail)}</span></div>`;
}
