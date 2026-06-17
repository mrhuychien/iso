import { call } from "../lib/api.js";
import { escapeHtml, formatNumber, pct } from "../lib/format.js";

let chartRef = null;

export async function render({ container }) {
  if (!(window.FS_CONTEXT && window.FS_CONTEXT.isManager)) {
    container.innerHTML = '<div class="app-alert app-alert-red">Chỉ quản lý ATTP được xem bảng điều khiển.</div>';
    return;
  }
  container.innerHTML = '<div class="app-card app-muted">Đang tải bảng điều khiển...</div>';
  try {
    const s = await call("hg_food_safety.api.analytics.dashboard_summary");
    const a = s.alerts || {}, today = s.today || {};
    const to = new Date().toISOString().slice(0, 10);
    const from = new Date(Date.now() - 30 * 864e5).toISOString().slice(0, 10);
    const k = await call("hg_food_safety.api.analytics.qc_kpis", { from_date: from, to_date: to });
    container.innerHTML = `
      <h2 class="app-h2">Bảng điều khiển ATTP</h2>
      <h3 class="app-h3">Cảnh báo</h3>
      <div class="app-grid">
        ${stat("Lô đang cô lập", a.batches_on_hold, a.batches_on_hold ? "red" : "")}
        ${stat("Sự không phù hợp", a.open_non_conformance)}
        ${stat("Mẫu đến hạn hủy", a.samples_due_disposal)}
        ${stat("Hiệu chuẩn < 30 ngày", a.calibration_due_30d)}
      </div>
      <h3 class="app-h3">KPI 30 ngày</h3>
      <div class="app-grid">
        ${stat("% đạt thành phẩm", k.finished_pass_rate === null ? "—" : pct(k.finished_pass_rate))}
        ${stat("% OPRP vượt", k.oprp_deviation_rate === null ? "—" : pct(k.oprp_deviation_rate))}
        ${stat("Mock recall (giờ)", k.mock_recall ? (k.mock_recall.avg_trace_hours ?? "—") : "—")}
      </div>
      <h3 class="app-h3">Ghi nhận hôm nay</h3>
      <div class="app-chart-wrap"><canvas id="app-today-chart"></canvas></div>`;
    await drawChart(today);
  } catch (e) {
    container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`;
  }
}

function stat(label, val, tone) {
  const v = typeof val === "number" ? formatNumber(val) : escapeHtml(String(val));
  return `<div class="app-stat ${tone === "red" ? "app-stat-red" : ""}">
    <div class="app-stat-val">${v}</div><div class="app-stat-label">${escapeHtml(label)}</div></div>`;
}

async function loadChartLib() {
  if (window.Chart) return window.Chart;
  await new Promise((res, rej) => {
    const s = document.createElement("script");
    s.src = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js";
    s.onload = res; s.onerror = rej; document.head.appendChild(s);
  });
  return window.Chart;
}

async function drawChart(today) {
  const Chart = await loadChartLib();
  const el = document.getElementById("app-today-chart");
  if (!el) return;
  if (chartRef) { chartRef.destroy(); chartRef = null; }
  chartRef = new Chart(el, {
    type: "bar",
    data: { labels: ["OPRP", "Thành phẩm", "Dị vật", "Vệ sinh"],
      datasets: [{ label: "Số bản ghi hôm nay",
        data: [today.oprp_logs, today.finished_checks, today.foreign_body_checks, today.sanitation_logs],
        backgroundColor: "#16a34a", borderRadius: 6 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
  });
}
