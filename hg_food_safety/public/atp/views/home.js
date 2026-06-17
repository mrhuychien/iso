import { call } from "../lib/api.js";
import { escapeHtml, formatNumber } from "../lib/format.js";

const ACTIONS = [
  { label: "Giam sat OPRP", icon: "ti-eye-check", dt: "oprp-monitoring-log" },
  { label: "Kiem di vat / dau do", icon: "ti-search", dt: "foreign-body-check-log" },
  { label: "Kiem thanh pham", icon: "ti-checkbox", dt: "quality-inspection" },
  { label: "Luu mau", icon: "ti-flask", dt: "sample-retention" },
  { label: "Nhat ky ve sinh", icon: "ti-spray", dt: "sanitation-log" },
  { label: "Kiem soat nuoc", icon: "ti-droplet", dt: "water-control-log" },
  { label: "Hang tai che", icon: "ti-recycle", dt: "rework-log" },
  { label: "Ket qua kiem nghiem", icon: "ti-microscope", dt: "lab-test-result" },
];

export async function render({ container }) {
  container.innerHTML = '<div class="app-card">Dang tai viec hom nay...</div>';
  let d = {};
  try {
    d = await call("hg_food_safety.api.portal.my_today");
  } catch (e) {
    container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`;
    return;
  }
  const done = d.done || {};
  const actions = ACTIONS.map((a) =>
    `<a class="app-action" href="/app/${a.dt}/new">
       <span class="app-action-ic">+</span>
       <span>${escapeHtml(a.label)}</span></a>`).join("");
  container.innerHTML = `
    <h2 class="app-h2">Ghi nhanh - ${escapeHtml(d.date || "")}</h2>
    <div class="app-actions">${actions}</div>

    <h3 class="app-h3">Da ghi hom nay</h3>
    <div class="app-grid">
      ${card("Giam sat OPRP", done.oprp)}
      ${card("Kiem di vat", done.foreign_body)}
      ${card("Nhat ky ve sinh", done.sanitation)}
      ${card("Kiem soat nuoc", done.water)}
    </div>
    <div class="app-alert ${d.batches_on_hold ? "app-alert-red" : ""}">
      Lo dang co lap: <b>${formatNumber(d.batches_on_hold)}</b>
    </div>`;
}

function card(label, val) {
  return `<div class="app-stat"><div class="app-stat-label">${escapeHtml(label)}</div>
    <div class="app-stat-val">${formatNumber(val)}</div></div>`;
}
