import { call } from "../lib/api.js";
import { escapeHtml } from "../lib/format.js";

const SHIFT = [{ v: "Sang", l: "Sáng" }, { v: "Chieu", l: "Chiều" }, { v: "Toi", l: "Tối" }];
const DD = [{ v: "Dat", l: "Đạt" }, { v: "Khong dat", l: "Không đạt" }];
const today = () => new Date().toISOString().slice(0, 10);

const FORMS = {
  oprp: { title: "Giám sát OPRP", doctype: "OPRP Monitoring Log", submit: true, fields: [
    { name: "log_date", label: "Ngày", type: "date", default: today, reqd: true },
    { name: "shift", label: "Ca", type: "select", options: SHIFT, reqd: true },
    { name: "batch_no", label: "Lô (Batch)", type: "link", target: "Batch", reqd: true },
    { name: "monitored_by", label: "Người giám sát", type: "link", target: "Employee", reqd: true },
    { name: "readings", label: "Chi tiết giám sát", type: "child", columns: [
      { name: "oprp_step", label: "OPRP/Công đoạn", type: "text" },
      { name: "parameter", label: "Thông số", type: "text" },
      { name: "action_limit", label: "Giới hạn hành động", type: "text" },
      { name: "result", label: "Kết quả", type: "text" },
      { name: "status", label: "Trạng thái", type: "select", options: DD },
    ] },
    { name: "corrective_action", label: "Hành động khắc phục (nếu vượt giới hạn)", type: "textarea" },
  ] },
  foreign_body: { title: "Kiểm dị vật / đầu dò", doctype: "Foreign Body Check Log", submit: true, fields: [
    { name: "log_date", label: "Ngày", type: "date", default: today, reqd: true },
    { name: "shift", label: "Ca", type: "select", options: SHIFT, reqd: true },
    { name: "batch_no", label: "Lô (Batch)", type: "link", target: "Batch" },
    { name: "stage", label: "Công đoạn", type: "text" },
    { name: "sieve_status", label: "Lưới sàng", type: "select", options: [
      { v: "Nguyen ven - dung co", l: "Nguyên vẹn - đúng cỡ" }, { v: "Bat thuong", l: "Bất thường" }] },
    { name: "metal_detector", label: "Đầu dò kim loại", type: "select", options: [
      { v: "Khong bao", l: "Không báo" }, { v: "Bao", l: "Báo" }, { v: "Khong ap dung", l: "Không áp dụng" }] },
    { name: "foreign_body_found", label: "Dị vật phát hiện", type: "textarea" },
    { name: "status", label: "Kết quả", type: "select", options: DD, reqd: true },
    { name: "action", label: "Hành động khắc phục", type: "textarea" },
    { name: "checked_by", label: "Người kiểm tra", type: "link", target: "Employee", reqd: true },
  ] },
  sanitation: { title: "Nhật ký vệ sinh", doctype: "Sanitation Log", submit: true, fields: [
    { name: "log_date", label: "Ngày", type: "date", default: today, reqd: true },
    { name: "shift", label: "Ca", type: "select", options: SHIFT, reqd: true },
    { name: "checked_by", label: "Người kiểm tra", type: "link", target: "Employee", reqd: true },
    { name: "items", label: "Hạng mục vệ sinh", type: "child", columns: [
      { name: "category", label: "Hạng mục", type: "select", options: [
        { v: "Ca nhan", l: "Cá nhân" }, { v: "Be mat - Thiet bi", l: "Bề mặt - Thiết bị" },
        { v: "Khu vuc", l: "Khu vực" }, { v: "Chat thai", l: "Chất thải" }] },
      { name: "content", label: "Nội dung", type: "text" },
      { name: "result", label: "Kết quả", type: "select", options: DD },
      { name: "action", label: "Khắc phục", type: "text" },
    ] },
  ] },
  water: { title: "Kiểm soát nước", doctype: "Water Control Log", submit: false, fields: [
    { name: "log_date", label: "Ngày", type: "date", default: today, reqd: true },
    { name: "shift", label: "Ca", type: "select", options: SHIFT, reqd: true },
    { name: "first_flush_done", label: "Đã xả nước đầu vòi", type: "check", default: 1 },
    { name: "sensory_ok", label: "Cảm quan (màu/mùi/độ trong)", type: "select", options: [
      { v: "Dat", l: "Đạt" }, { v: "Bat thuong", l: "Bất thường" }] },
    { name: "note", label: "Ghi chú", type: "textarea" },
    { name: "recorded_by", label: "Người ghi", type: "link", target: "Employee", reqd: true },
  ] },
  sample: { title: "Lưu mẫu", doctype: "Sample Retention", submit: false, fields: [
    { name: "retention_date", label: "Ngày lưu", type: "date", default: today, reqd: true },
    { name: "item", label: "Sản phẩm", type: "link", target: "Item" },
    { name: "batch_no", label: "Lô (Batch)", type: "link", target: "Batch", reqd: true },
    { name: "qty", label: "Số lượng mẫu", type: "int" },
    { name: "location", label: "Vị trí lưu", type: "text" },
    { name: "kept_by", label: "Người lưu", type: "link", target: "Employee" },
  ] },
  rework: { title: "Hàng tái chế (rework)", doctype: "Rework Log", submit: false, fields: [
    { name: "log_date", label: "Ngày", type: "date", default: today, reqd: true },
    { name: "item", label: "Sản phẩm", type: "link", target: "Item" },
    { name: "source_batch", label: "Lô gốc", type: "link", target: "Batch", reqd: true },
    { name: "rework_qty", label: "Khối lượng rework (kg)", type: "int" },
    { name: "target_batch", label: "Lô đưa vào", type: "link", target: "Batch", reqd: true },
    { name: "like_into_like", label: "Cùng loại vào cùng loại", type: "check", default: 1 },
    { name: "approved_by", label: "Người duyệt", type: "link", target: "Employee" },
  ] },
  lab: { title: "Kết quả kiểm nghiệm", doctype: "Lab Test Result", submit: false, fields: [
    { name: "sample_date", label: "Ngày lấy mẫu", type: "date", default: today, reqd: true },
    { name: "target_type", label: "Đối tượng", type: "select", options: [
      { v: "San pham", l: "Sản phẩm" }, { v: "Nuoc", l: "Nước" }, { v: "Nguyen lieu", l: "Nguyên liệu" }], reqd: true },
    { name: "item", label: "Sản phẩm/NL", type: "link", target: "Item" },
    { name: "batch_no", label: "Lô", type: "link", target: "Batch" },
    { name: "parameter", label: "Chỉ tiêu", type: "text" },
    { name: "limit_basis", label: "Giới hạn / Căn cứ (QCVN)", type: "text" },
    { name: "result", label: "Kết quả", type: "text" },
    { name: "status", label: "Đánh giá", type: "select", options: DD },
    { name: "lab", label: "Phòng thử nghiệm (ISO 17025)", type: "text" },
  ] },
};

export async function render({ container, query }) {
  const spec = FORMS[query.dt];
  if (!spec) { container.innerHTML = '<div class="app-alert app-alert-red">Không tìm thấy biểu mẫu.</div>'; return; }
  const state = {};
  container.innerHTML = `
    <div class="app-form-head">
      <a class="app-back" href="#/">← Quay lại</a>
      <h2 class="app-h2">${escapeHtml(spec.title)}</h2>
    </div>
    <div class="app-form" id="app-form"></div>
    <div id="app-form-msg"></div>
    <button class="app-btn app-btn-lg" id="app-save">Lưu${spec.submit ? " & gửi" : ""}</button>`;
  const form = container.querySelector("#app-form");
  spec.fields.forEach((f) => form.appendChild(renderField(f, state)));
  container.querySelector("#app-save").addEventListener("click", () => save(spec, state, container));
}

function group(label, reqd) {
  const g = document.createElement("div");
  g.className = "app-fg";
  g.innerHTML = `<label class="app-label">${escapeHtml(label)}${reqd ? ' <span class="app-req">*</span>' : ""}</label>`;
  return g;
}

function renderField(f, state) {
  const g = group(f.label, f.reqd);
  if (f.type === "date") {
    const i = inp("date"); i.value = typeof f.default === "function" ? f.default() : "";
    state[f.name] = i.value; i.addEventListener("input", () => (state[f.name] = i.value)); g.appendChild(i);
  } else if (f.type === "text" || f.type === "int") {
    const i = inp(f.type === "int" ? "number" : "text");
    i.addEventListener("input", () => (state[f.name] = i.value)); g.appendChild(i);
  } else if (f.type === "textarea") {
    const t = document.createElement("textarea"); t.className = "app-input"; t.rows = 2;
    t.addEventListener("input", () => (state[f.name] = t.value)); g.appendChild(t);
  } else if (f.type === "check") {
    const w = document.createElement("label"); w.className = "app-check";
    const c = document.createElement("input"); c.type = "checkbox"; c.checked = !!f.default;
    state[f.name] = f.default ? 1 : 0;
    c.addEventListener("change", () => (state[f.name] = c.checked ? 1 : 0));
    w.appendChild(c); w.appendChild(document.createTextNode(" " + f.label));
    g.innerHTML = ""; g.appendChild(w);
  } else if (f.type === "select") {
    const s = document.createElement("select"); s.className = "app-input";
    s.innerHTML = '<option value=""></option>' + f.options.map((o) =>
      `<option value="${escapeHtml(o.v)}">${escapeHtml(o.l)}</option>`).join("");
    s.addEventListener("change", () => (state[f.name] = s.value)); g.appendChild(s);
  } else if (f.type === "link") {
    g.appendChild(linkField(f, state));
  } else if (f.type === "child") {
    g.appendChild(childTable(f, state));
  }
  return g;
}

function inp(type) { const i = document.createElement("input"); i.type = type; i.className = "app-input"; return i; }

function linkField(f, state) {
  const wrap = document.createElement("div"); wrap.className = "app-link";
  const i = inp("text"); i.placeholder = "Gõ để tìm...";
  const box = document.createElement("div"); box.className = "app-link-box";
  let timer;
  i.addEventListener("input", () => {
    state[f.name] = i.value;
    clearTimeout(timer);
    timer = setTimeout(async () => {
      try {
        const rows = await call("hg_food_safety.api.portal.search_link", { doctype: f.target, txt: i.value });
        box.innerHTML = rows.map((r) => `<div class="app-link-opt" data-v="${escapeHtml(r.value)}">${escapeHtml(r.label)}</div>`).join("");
        box.querySelectorAll(".app-link-opt").forEach((o) =>
          o.addEventListener("click", () => { i.value = o.dataset.v; state[f.name] = o.dataset.v; box.innerHTML = ""; }));
      } catch (e) { box.innerHTML = ""; }
    }, 280);
  });
  wrap.appendChild(i); wrap.appendChild(box); return wrap;
}

function childTable(f, state) {
  state[f.name] = [];
  const wrap = document.createElement("div");
  const tbl = document.createElement("table"); tbl.className = "app-ctable";
  tbl.innerHTML = `<thead><tr>${f.columns.map((c) => `<th>${escapeHtml(c.label)}</th>`).join("")}<th></th></tr></thead><tbody></tbody>`;
  const body = tbl.querySelector("tbody");
  const addRow = () => {
    const row = {}; state[f.name].push(row);
    const tr = document.createElement("tr");
    f.columns.forEach((c) => {
      const td = document.createElement("td");
      let ctrl;
      if (c.type === "select") {
        ctrl = document.createElement("select"); ctrl.className = "app-cinput";
        ctrl.innerHTML = '<option value=""></option>' + c.options.map((o) => `<option value="${escapeHtml(o.v)}">${escapeHtml(o.l)}</option>`).join("");
        ctrl.addEventListener("change", () => (row[c.name] = ctrl.value));
      } else { ctrl = inp("text"); ctrl.className = "app-cinput"; ctrl.addEventListener("input", () => (row[c.name] = ctrl.value)); }
      td.appendChild(ctrl); tr.appendChild(td);
    });
    const del = document.createElement("td");
    const b = document.createElement("button"); b.className = "app-x"; b.textContent = "×";
    b.addEventListener("click", () => { const idx = state[f.name].indexOf(row); if (idx > -1) state[f.name].splice(idx, 1); tr.remove(); });
    del.appendChild(b); tr.appendChild(del); body.appendChild(tr);
  };
  const add = document.createElement("button"); add.className = "app-btn-sm"; add.textContent = "+ Thêm dòng";
  add.addEventListener("click", addRow);
  wrap.appendChild(tbl); wrap.appendChild(add); addRow();
  return wrap;
}

async function save(spec, state, container) {
  const msg = container.querySelector("#app-form-msg");
  const btn = container.querySelector("#app-save");
  for (const f of spec.fields) {
    if (f.reqd && !state[f.name]) { msg.innerHTML = `<div class="app-alert app-alert-red">Thiếu: ${escapeHtml(f.label)}</div>`; return; }
  }
  btn.disabled = true; msg.innerHTML = '<div class="app-alert">Đang lưu...</div>';
  try {
    const r = await call("hg_food_safety.api.portal.create_record", {
      doctype: spec.doctype, payload: JSON.stringify(state), submit: spec.submit ? 1 : 0 });
    msg.innerHTML = `<div class="app-alert app-alert-ok">Đã lưu: <b>${escapeHtml(r.name)}</b></div>`;
    setTimeout(() => { location.hash = "#/"; }, 900);
  } catch (e) {
    btn.disabled = false;
    msg.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml((e.message || "").replace(/<[^>]+>/g, " "))}</div>`;
  }
}
