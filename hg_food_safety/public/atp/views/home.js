import { call } from "../lib/api.js";
import { escapeHtml, formatNumber } from "../lib/format.js";

const ACTIONS = [
  { label: "Giám sát OPRP", dt: "oprp", ic: "M9 11l3 3 8-8" },
  { label: "Kiểm dị vật", dt: "foreign_body", ic: "M21 21l-5-5M3 10a7 7 0 1014 0 7 7 0 00-14 0" },
  { label: "Kết quả kiểm nghiệm", dt: "lab", ic: "M9 11l3 3 8-8" },
  { label: "Lưu mẫu", dt: "sample", ic: "M6 2v6l-3 9a2 2 0 002 3h14a2 2 0 002-3l-3-9V2" },
  { label: "Nhật ký vệ sinh", dt: "sanitation", ic: "M3 12h18M12 3v18" },
  { label: "Kiểm soát nước", dt: "water", ic: "M12 2s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z" },
  { label: "Hàng tái chế", dt: "rework", ic: "M4 4v6h6M20 20v-6h-6M20 8a8 8 0 00-15-2M4 16a8 8 0 0015 2" },
];

export async function render({ container }) {
  container.innerHTML = '<div class="app-card app-muted">Đang tải việc hôm nay...</div>';
  let d = {};
  try { d = await call("hg_food_safety.api.portal.my_today"); }
  catch (e) { container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }
  const done = d.done || {};
  const actions = ACTIONS.map((a) =>
    `<a class="app-action" href="#/entry?dt=${a.dt}">
      <span class="app-action-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${a.ic}"/></svg></span>
      <span class="app-action-lb">${escapeHtml(a.label)}</span></a>`).join("");
  const hold = d.batches_on_hold || 0;
  container.innerHTML = `
    ${hold ? `<div class="app-banner app-banner-red"><b>${formatNumber(hold)}</b> lô đang bị cô lập — cần xử lý</div>` : ""}
    <h2 class="app-h2">Ghi nhanh</h2>
    <div class="app-actions">${actions}</div>
    <h3 class="app-h3">Đã ghi hôm nay</h3>
    <div class="app-grid">
      ${stat("Giám sát OPRP", done.oprp)}
      ${stat("Kiểm dị vật", done.foreign_body)}
      ${stat("Nhật ký vệ sinh", done.sanitation)}
      ${stat("Kiểm soát nước", done.water)}
    </div>`;
}

function stat(label, val) {
  return `<div class="app-stat"><div class="app-stat-val">${formatNumber(val)}</div>
    <div class="app-stat-label">${escapeHtml(label)}</div></div>`;
}
