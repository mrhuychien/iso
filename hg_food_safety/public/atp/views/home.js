import { call } from "../lib/api.js";
import { escapeHtml, formatNumber } from "../lib/format.js";

const ACTIONS = [
  { label: "Giám sát OPRP", dt: "oprp", ic: "visibility" },
  { label: "Kiểm dị vật", dt: "foreign_body", ic: "search" },
  { label: "Kết quả kiểm nghiệm", dt: "lab", ic: "science" },
  { label: "Lưu mẫu", dt: "sample", ic: "inventory_2" },
  { label: "Nhật ký vệ sinh", dt: "sanitation", ic: "clean_hands" },
  { label: "Kiểm soát nước", dt: "water", ic: "water_drop" },
  { label: "Hàng tái chế", dt: "rework", ic: "recycling" },
];

export async function render({ container }) {
  container.innerHTML = '<div class="app-card app-muted">Đang tải việc hôm nay...</div>';
  let d = {};
  try { d = await call("hg_food_safety.api.portal.my_today"); }
  catch (e) { container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }
  const done = d.done || {};
  const actions = ACTIONS.map((a) =>
    `<a class="app-action" href="#/entry?dt=${a.dt}">
      <span class="app-action-ic"><span class="material-symbols-outlined">${a.ic}</span></span>
      <span class="app-action-lb">${escapeHtml(a.label)}</span></a>`).join("");
  const hold = d.batches_on_hold || 0;
  container.innerHTML = `
    ${hold ? `<div class="app-banner app-banner-red"><span class="material-symbols-outlined">warning</span><span><b>${formatNumber(hold)}</b> lô đang bị cô lập — cần xử lý</span></div>` : ""}
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
