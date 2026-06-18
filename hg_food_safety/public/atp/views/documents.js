import { call, uploadFile } from "../lib/api.js";
import { escapeHtml } from "../lib/format.js";

const isMgr = () => !!(window.FS_CONTEXT && window.FS_CONTEXT.isManager);

const CAT_ORDER = [
  "Chinh sach - Muc tieu", "So tay - PRP/SSOP", "Ke hoach (HACCP/OPRP/KN/SL)",
  "Quy trinh (QT)", "Quy dinh (QD)", "Bieu mau - Ho so (BM)",
  "Danh muc - Dinh muc", "Tai lieu ben ngoai",
];
const CAT_VI = {
  "Chinh sach - Muc tieu": "Chính sách & Mục tiêu",
  "So tay - PRP/SSOP": "Sổ tay & PRP/SSOP",
  "Ke hoach (HACCP/OPRP/KN/SL)": "Kế hoạch (HACCP/OPRP/KN/SL)",
  "Quy trinh (QT)": "Quy trình (QT)",
  "Quy dinh (QD)": "Quy định (QĐ)",
  "Bieu mau - Ho so (BM)": "Biểu mẫu & Hồ sơ (BM)",
  "Danh muc - Dinh muc": "Danh mục & Định mức",
  "Tai lieu ben ngoai": "Tài liệu bên ngoài (pháp luật, tiêu chuẩn)",
  "": "Chưa phân nhóm",
};
const TYPE_VI = { "Noi bo": "Nội bộ", "Ben ngoai": "Bên ngoài" };
const STATUS_VI = { "Hieu luc": "Hiệu lực", "Da thay the": "Đã thay thế", "Het hieu luc": "Hết hiệu lực" };
const opt = (map, sel) => Object.entries(map).filter(([v]) => v !== "")
  .map(([v, l]) => `<option value="${escapeHtml(v)}"${v === sel ? " selected" : ""}>${escapeHtml(l)}</option>`).join("");
const CAT_OPTS = (sel) => CAT_ORDER.map((v) => `<option value="${escapeHtml(v)}"${v === sel ? " selected" : ""}>${escapeHtml(CAT_VI[v])}</option>`).join("");

let DOCS = [];

export async function render({ container }) {
  container.innerHTML = '<div class="app-card app-muted">Đang tải danh mục tài liệu...</div>';
  try { DOCS = await call("hg_food_safety.api.portal.documents"); }
  catch (e) { container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }

  let catalog;
  if (!DOCS.length) {
    catalog = '<div class="app-alert">Chưa có tài liệu nào trong danh mục.</div>';
  } else {
    const groups = {};
    DOCS.forEach((d) => { const k = d.doc_category || ""; (groups[k] || (groups[k] = [])).push(d); });
    const keys = CAT_ORDER.filter((k) => groups[k]).concat(Object.keys(groups).filter((k) => !CAT_ORDER.includes(k)));
    catalog = keys.map((k) => `
      <h3 class="app-h3">${escapeHtml(CAT_VI[k] || k)} <span class="app-badge">${groups[k].length}</span></h3>
      <div class="app-doclist">${groups[k].map(docRow).join("")}</div>`).join("");
  }

  const adder = isMgr() ? `
    <h3 class="app-h3">Thêm tài liệu vào danh mục</h3>
    <div class="app-form">
      <div class="app-fg"><label class="app-label">Tên tài liệu <span class="app-req">*</span></label><input class="app-input" id="a-name"></div>
      <div class="app-row" style="margin:0">
        <div class="app-fg" style="flex:1"><label class="app-label">Mã tài liệu</label><input class="app-input" id="a-code" placeholder="VD: QT.09"></div>
        <div class="app-fg" style="flex:1"><label class="app-label">Phiên bản</label><input class="app-input" id="a-ver" placeholder="vd: 01"></div>
      </div>
      <div class="app-fg"><label class="app-label">Nhóm tài liệu</label><select class="app-input" id="a-cat">${CAT_OPTS("Bieu mau - Ho so (BM)")}</select></div>
      <div class="app-fg"><label class="app-label">Loại</label><select class="app-input" id="a-type">${opt(TYPE_VI)}</select></div>
      <div class="app-fg"><label class="app-label">Tệp (PDF/ảnh/Word) — tùy chọn</label><input class="app-input" type="file" id="a-file"></div>
      <button class="app-btn app-btn-lg" id="a-go">Thêm vào danh mục</button>
      <div id="a-msg"></div>
    </div>` : "";

  container.innerHTML = `
    <h2 class="app-h2">Danh mục tài liệu</h2>
    <div class="app-muted" style="margin:-8px 0 6px;font-size:13px">${DOCS.length} tài liệu — ISO 22000</div>
    ${catalog}
    ${adder}`;

  container.querySelectorAll("[data-view]").forEach((b) => {
    b.addEventListener("click", () => openDetail(b.dataset.view, container));
    b.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openDetail(b.dataset.view, container); } });
  });
  container.querySelectorAll("[data-hist]").forEach((b) =>
    b.addEventListener("click", (e) => { e.stopPropagation(); openHistory(b.dataset.hist); }));
  container.querySelectorAll("[data-edit]").forEach((b) =>
    b.addEventListener("click", (e) => { e.stopPropagation(); openEditor(b.dataset.edit, container); }));
  if (isMgr()) container.querySelector("#a-go").addEventListener("click", () => doAdd(container));
}

function docRow(d) {
  const status = STATUS_VI[d.status] || d.status || "";
  const meta = [d.doc_code, d.version ? "v" + d.version : "", status, d.location]
    .filter(Boolean).map(escapeHtml).join(" · ");
  const read = d.attachment
    ? `<a class="app-btn-sm" href="${escapeHtml(d.attachment)}" target="_blank" rel="noopener" title="Mở tệp"><span class="material-symbols-outlined" style="font-size:18px">visibility</span></a>`
    : "";
  return `<div class="app-doc app-doc-click" data-view="${escapeHtml(d.name)}" role="button" tabindex="0">
    <div class="app-doc-ic"><span class="material-symbols-outlined">description</span></div>
    <div class="app-doc-main">
      <div class="app-doc-name">${escapeHtml(d.doc_name || d.name)}</div>
      <div class="app-doc-meta">${meta}</div>
    </div>
    <div class="app-doc-act">${read}<span class="material-symbols-outlined app-doc-chev">chevron_right</span></div></div>`;
}

function kv(label, value) {
  if (!value) return "";
  return `<div class="app-kv"><span class="app-kv-l">${escapeHtml(label)}</span><span class="app-kv-v">${escapeHtml(value)}</span></div>`;
}

function openDetail(name, container) {
  const d = DOCS.find((x) => x.name === name);
  if (!d) return;
  const tags = [
    d.doc_category ? `<span class="app-tag">${escapeHtml(CAT_VI[d.doc_category] || d.doc_category)}</span>` : "",
    `<span class="app-tag">${escapeHtml(TYPE_VI[d.doc_type] || d.doc_type || "")}</span>`,
    `<span class="app-tag app-tag-${d.status === "Hieu luc" ? "ok" : "muted"}">${escapeHtml(STATUS_VI[d.status] || d.status || "")}</span>`,
  ].join("");
  const body = `
    <div class="app-detail-head">
      <div class="app-detail-title">${escapeHtml(d.doc_name || d.name)}</div>
      ${d.doc_code ? `<div class="app-detail-code">${escapeHtml(d.doc_code)}</div>` : ""}
      <div class="app-detail-tags">${tags}</div>
    </div>
    <div class="app-kvlist">
      ${kv("Phiên bản", d.version)}
      ${kv("Nơi lưu", d.location)}
      ${kv("Thời gian lưu", d.retention)}
      ${kv("Ngày hiệu lực", d.effective_date)}
      ${kv("Cập nhật cuối", (d.modified || "").replace("T", " ").slice(0, 16))}
      ${kv("Số lần cập nhật", String(d.change_count || 0))}
    </div>
    ${d.summary ? `<div class="app-detail-sum"><div class="app-kv-l" style="margin-bottom:6px">Tóm tắt / Ghi chú</div>${escapeHtml(d.summary)}</div>` : ""}
    <div class="app-detail-act">
      ${d.attachment
        ? `<a class="app-btn" href="${escapeHtml(d.attachment)}" target="_blank" rel="noopener"><span class="material-symbols-outlined" style="font-size:19px">visibility</span>Đọc tệp</a>`
        : `<span class="app-alert" style="margin:0;flex:1">Tài liệu chưa đính kèm tệp.</span>`}
      <button class="app-btn-sm app-btn-ghost" data-d-hist><span class="material-symbols-outlined" style="font-size:18px">history</span>Lịch sử (${escapeHtml(String(d.change_count || 0))})</button>
      ${isMgr() ? '<button class="app-btn-sm app-btn-ghost" data-d-edit><span class="material-symbols-outlined" style="font-size:18px">edit</span>Sửa</button>' : ""}
    </div>`;
  const { ov, close } = modal("Chi tiết tài liệu", body);
  ov.querySelector("[data-d-hist]").addEventListener("click", () => openHistory(name));
  const eb = ov.querySelector("[data-d-edit]");
  if (eb) eb.addEventListener("click", () => { close(); openEditor(name, container); });
}

/* ---------- Modal helpers ---------- */
function modal(title, bodyHtml) {
  const ov = document.createElement("div");
  ov.className = "app-modal-ov";
  ov.innerHTML = `<div class="app-modal" role="dialog">
    <div class="app-modal-head"><span>${escapeHtml(title)}</span><button class="app-modal-x" aria-label="Đóng">×</button></div>
    <div class="app-modal-body">${bodyHtml}</div></div>`;
  document.body.appendChild(ov);
  const close = () => ov.remove();
  ov.addEventListener("click", (e) => { if (e.target === ov) close(); });
  ov.querySelector(".app-modal-x").addEventListener("click", close);
  return { ov, close };
}

async function openHistory(name) {
  const { ov } = modal("Lịch sử cập nhật", '<div class="app-muted">Đang tải...</div>');
  const body = ov.querySelector(".app-modal-body");
  try {
    const rows = await call("hg_food_safety.api.portal.document_history", { name });
    body.innerHTML = rows.length ? `<div class="app-histlist">${rows.map((r) => `
      <div class="app-hist">
        <div class="app-hist-top"><span class="app-hist-act">${escapeHtml(r.action || "")}</span>
          <span class="app-hist-when">${escapeHtml((r.changed_on || "").replace("T", " ").slice(0, 16))}</span></div>
        <div class="app-hist-meta">${escapeHtml(r.changed_by || "")}${r.version ? " · v" + escapeHtml(r.version) : ""}</div>
        ${r.note ? `<div class="app-hist-note">${escapeHtml(r.note)}</div>` : ""}
      </div>`).join("")}</div>` : '<div class="app-alert">Chưa có lịch sử cập nhật.</div>';
  } catch (e) { body.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; }
}

function openEditor(name, container) {
  const d = DOCS.find((x) => x.name === name) || {};
  const { ov, close } = modal("Sửa tài liệu", `
    <div class="app-form" style="box-shadow:none;border:none;padding:0">
      <div class="app-fg"><label class="app-label">Tên tài liệu <span class="app-req">*</span></label><input class="app-input" id="e-name" value="${escapeHtml(d.doc_name || "")}"></div>
      <div class="app-row" style="margin:0">
        <div class="app-fg" style="flex:1"><label class="app-label">Mã</label><input class="app-input" id="e-code" value="${escapeHtml(d.doc_code || "")}"></div>
        <div class="app-fg" style="flex:1"><label class="app-label">Phiên bản</label><input class="app-input" id="e-ver" value="${escapeHtml(d.version || "")}"></div>
      </div>
      <div class="app-fg"><label class="app-label">Nhóm tài liệu</label><select class="app-input" id="e-cat">${CAT_OPTS(d.doc_category || "")}</select></div>
      <div class="app-row" style="margin:0">
        <div class="app-fg" style="flex:1"><label class="app-label">Loại</label><select class="app-input" id="e-type">${opt(TYPE_VI, d.doc_type || "Noi bo")}</select></div>
        <div class="app-fg" style="flex:1"><label class="app-label">Tình trạng</label><select class="app-input" id="e-status">${opt(STATUS_VI, d.status || "Hieu luc")}</select></div>
      </div>
      <div class="app-row" style="margin:0">
        <div class="app-fg" style="flex:1"><label class="app-label">Nơi lưu</label><input class="app-input" id="e-loc" value="${escapeHtml(d.location || "")}"></div>
        <div class="app-fg" style="flex:1"><label class="app-label">Thời gian lưu</label><input class="app-input" id="e-ret" value="${escapeHtml(d.retention || "")}"></div>
      </div>
      <div class="app-fg"><label class="app-label">Tóm tắt / Ghi chú nội dung</label><textarea class="app-input" id="e-sum" rows="2">${escapeHtml(d.summary || "")}</textarea></div>
      <div class="app-fg"><label class="app-label">Thay tệp (tùy chọn)</label><input class="app-input" type="file" id="e-file"></div>
      <div class="app-fg"><label class="app-label">Lý do / ghi chú cập nhật</label><input class="app-input" id="e-note" placeholder="VD: cập nhật phiên bản mới"></div>
      <button class="app-btn app-btn-lg" id="e-save">Lưu cập nhật</button>
      <div id="e-msg"></div>
    </div>`);
  ov.querySelector("#e-save").addEventListener("click", async () => {
    const name2 = (ov.querySelector("#e-name").value || "").trim();
    const msg = ov.querySelector("#e-msg");
    if (!name2) { msg.innerHTML = '<div class="app-alert app-alert-red">Cần tên tài liệu.</div>'; return; }
    const btn = ov.querySelector("#e-save"); btn.disabled = true;
    msg.innerHTML = '<div class="app-alert">Đang lưu...</div>';
    try {
      const fileEl = ov.querySelector("#e-file");
      let attachment;
      if (fileEl.files.length) { const up = await uploadFile(fileEl.files[0], 0); attachment = up.file_url; }
      await call("hg_food_safety.api.portal.update_document", {
        name, doc_name: name2, doc_code: ov.querySelector("#e-code").value.trim(),
        doc_category: ov.querySelector("#e-cat").value, doc_type: ov.querySelector("#e-type").value,
        version: ov.querySelector("#e-ver").value.trim(), status: ov.querySelector("#e-status").value,
        location: ov.querySelector("#e-loc").value.trim(), retention: ov.querySelector("#e-ret").value.trim(),
        summary: ov.querySelector("#e-sum").value.trim(), note: ov.querySelector("#e-note").value.trim(),
        attachment,
      });
      close();
      render({ container });
    } catch (e) {
      btn.disabled = false;
      msg.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml((e.message || "").replace(/<[^>]+>/g, " "))}</div>`;
    }
  });
}

async function doAdd(container) {
  const name = container.querySelector("#a-name").value.trim();
  const msg = container.querySelector("#a-msg");
  if (!name) { msg.innerHTML = '<div class="app-alert app-alert-red">Cần tên tài liệu.</div>'; return; }
  const btn = container.querySelector("#a-go"); btn.disabled = true;
  msg.innerHTML = '<div class="app-alert">Đang lưu...</div>';
  try {
    const fileEl = container.querySelector("#a-file");
    let attachment = null;
    if (fileEl.files.length) { const up = await uploadFile(fileEl.files[0], 0); attachment = up.file_url; }
    await call("hg_food_safety.api.portal.create_document", {
      doc_name: name, doc_code: container.querySelector("#a-code").value.trim(),
      doc_category: container.querySelector("#a-cat").value, doc_type: container.querySelector("#a-type").value,
      version: container.querySelector("#a-ver").value.trim(), attachment });
    msg.innerHTML = '<div class="app-alert app-alert-ok">Đã thêm vào danh mục.</div>';
    setTimeout(() => render({ container }), 700);
  } catch (e) {
    btn.disabled = false;
    msg.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml((e.message || "").replace(/<[^>]+>/g, " "))}</div>`;
  }
}
