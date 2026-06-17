import { call } from "../lib/api.js";
import { escapeHtml } from "../lib/format.js";

export async function render({ container, query }) {
  const batch = query.batch || "";
  container.innerHTML = `
    <h2 class="app-h2">Truy xuất theo lô</h2>
    <div class="app-row">
      <input id="app-batch" class="app-input" placeholder="Nhập mã lô (Batch)" value="${escapeHtml(batch)}">
      <button id="app-go" class="app-btn">Truy xuất</button>
    </div>
    <div id="app-trace-result"></div>`;
  const go = () => {
    const b = document.getElementById("app-batch").value.trim();
    if (b) location.hash = "#/trace?batch=" + encodeURIComponent(b);
  };
  container.querySelector("#app-go").addEventListener("click", go);
  container.querySelector("#app-batch").addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
  if (batch) await load(batch, container.querySelector("#app-trace-result"));
}

async function load(batch, target) {
  target.innerHTML = '<div class="app-card app-muted">Đang tải...</div>';
  try {
    const d = await call("hg_food_safety.api.trace.by_batch", { batch_no: batch });
    const hold = (d.batch_status || "").toLowerCase().indexOf("co lap") > -1;
    const sec = (title, rows, fmt) => `
      <div class="app-tl-sec"><div class="app-tl-title">${escapeHtml(title)} <span class="app-badge">${(rows || []).length}</span></div>
      ${(rows || []).map(fmt).join("") || '<div class="app-tl-empty">— không có —</div>'}</div>`;
    target.innerHTML = `
      <div class="app-banner ${hold ? "app-banner-red" : "app-banner-ok"}">Trạng thái lô: <b>${escapeHtml(d.batch_status || "—")}</b></div>
      ${sec("Giám sát OPRP", d.oprp, (r) => line(r.name, r.log_date + " · " + r.shift + (r.has_deviation ? " · VƯỢT" : "")))}
      ${sec("Kiểm dị vật", d.foreign_body, (r) => line(r.name, r.log_date + " · " + r.status))}
      ${sec("Kiểm thành phẩm", d.finished_inspection, (r) => line(r.name, (r.item_code || "") + " · " + r.status))}
      ${sec("Lưu mẫu", d.sample_retention, (r) => line(r.name, r.retention_date + " → " + (r.keep_until || "")))}`;
  } catch (e) {
    target.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`;
  }
}

function line(name, detail) {
  return `<div class="app-tl-row"><span class="app-tl-name">${escapeHtml(name)}</span>
    <span class="app-tl-detail">${escapeHtml(detail)}</span></div>`;
}
