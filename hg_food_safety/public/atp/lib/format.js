export function escapeHtml(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

export function formatNumber(n) {
  if (n === null || n === undefined || n === "") return "-";
  return new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 }).format(Math.round(Number(n)));
}

export function pct(n) {
  if (n === null || n === undefined) return "-";
  return Math.round(Number(n) * 10) / 10 + "%";
}
