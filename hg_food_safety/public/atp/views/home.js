import { call } from "../lib/api.js";
import { escapeHtml, formatNumber } from "../lib/format.js";

export async function render({ container }) {
  container.innerHTML = '<div class="app-card app-muted">Đang tải công việc...</div>';
  let d = {};
  try { d = await call("hg_food_safety.api.portal.today_tasks"); }
  catch (e) { container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }

  const hold = d.batches_on_hold || 0;
  const groups = (d.groups || []).map((g) => `
    <h3 class="app-h3"><span class="material-symbols-outlined app-h3-ic">${escapeHtml(g.icon || "task_alt")}</span>
      ${escapeHtml(g.group)} <span class="app-badge">${g.tasks.length}</span></h3>
    <div class="app-tasklist">${g.tasks.map(taskRow).join("")}</div>`).join("");

  const overdue = d.overdue_count || 0;
  const sub = `${formatNumber(d.open_count)} việc cần làm${overdue ? ` · <b class="app-sub-late">${formatNumber(overdue)} trễ hạn</b>` : ""}`;

  container.innerHTML = `
    ${hold ? `<div class="app-banner app-banner-red"><span class="material-symbols-outlined">warning</span><span><b>${formatNumber(hold)}</b> lô đang bị cô lập — cần xử lý</span></div>` : ""}
    <h2 class="app-h2">Công việc cần làm</h2>
    ${d.open_count ? `<div class="app-muted" style="margin:-8px 0 6px;font-size:13px">${sub}</div>` : ""}
    ${groups || '<div class="app-alert app-alert-ok">Không còn công việc nào đang chờ. 👍</div>'}`;

  container.querySelectorAll("[data-done]").forEach((b) =>
    b.addEventListener("click", async () => {
      b.disabled = true; b.textContent = "Đang lưu...";
      try { await call("hg_food_safety.api.portal.mark_task_done", { log: b.dataset.done }); render({ container }); }
      catch (e) { b.disabled = false; b.textContent = "Đánh dấu đã làm"; alert(e.message); }
    }));
}

function taskRow(t) {
  const late = t.status === "Tre";
  const chip = `<span class="app-chip ${late ? "app-chip-red" : "app-chip-gray"}">${late ? "Trễ" : "Chờ"}</span>`;
  const action = t.linked_form
    ? `<a class="app-btn-sm" href="#/entry?dt=${escapeHtml(t.linked_form)}">Ghi</a>`
    : `<button class="app-btn-sm" data-done="${escapeHtml(t.name)}">Đánh dấu đã làm</button>`;
  const missed = Number(t.missed) > 0
    ? ` <span class="app-task-freq">· bỏ lỡ ${escapeHtml(String(t.missed))} kỳ</span>` : "";
  return `<div class="app-task">
    <div class="app-task-main"><div class="app-task-title">${escapeHtml(t.title)}</div>
      <div class="app-task-meta">${chip} <span class="app-task-freq">${escapeHtml(t.frequency)}</span>${missed}</div></div>
    <div class="app-task-act">${action}</div></div>`;
}
