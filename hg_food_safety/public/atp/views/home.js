import { call } from "../lib/api.js";
import { escapeHtml, formatNumber } from "../lib/format.js";

export async function render({ container }) {
  container.innerHTML = '<div class="app-card">Dang tai viec hom nay...</div>';
  try {
    const d = await call("hg_food_safety.api.portal.my_today");
    const done = d.done || {};
    container.innerHTML = `
      <h2 class="app-h2">Viec hom nay - ${escapeHtml(d.date)}</h2>
      <div class="app-grid">
        ${card("Giam sat OPRP", done.oprp)}
        ${card("Kiem di vat", done.foreign_body)}
        ${card("Nhat ky ve sinh", done.sanitation)}
        ${card("Kiem soat nuoc", done.water)}
      </div>
      <div class="app-alert ${d.batches_on_hold ? "app-alert-red" : ""}">
        Lo dang co lap: <b>${formatNumber(d.batches_on_hold)}</b>
      </div>`;
  } catch (e) {
    container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`;
  }
}

function card(label, val) {
  return `<div class="app-stat"><div class="app-stat-label">${escapeHtml(label)}</div>
    <div class="app-stat-val">${formatNumber(val)}</div></div>`;
}
