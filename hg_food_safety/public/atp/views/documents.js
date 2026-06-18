import { call, uploadFile } from "../lib/api.js";
import { escapeHtml } from "../lib/format.js";

const isMgr = () => !!(window.FS_CONTEXT && window.FS_CONTEXT.isManager);

const TYPE_VI = { "Noi bo": "Tài liệu nội bộ", "Ben ngoai": "Tài liệu bên ngoài (pháp luật, tiêu chuẩn)" };
const TYPE_ORDER = ["Noi bo", "Ben ngoai"];
const STATUS_VI = { "Hieu luc": "Hiệu lực", "Da thay the": "Đã thay thế", "Het hieu luc": "Hết hiệu lực" };

export async function render({ container }) {
  container.innerHTML = '<div class="app-card app-muted">Đang tải danh mục tài liệu...</div>';
  let docs = [];
  try { docs = await call("hg_food_safety.api.portal.documents"); }
  catch (e) { container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }

  let catalog = "";
  if (!docs.length) {
    catalog = '<div class="app-alert">Chưa có tài liệu nào trong danh mục.</div>';
  } else {
    const groups = {};
    docs.forEach((d) => { (groups[d.doc_type] || (groups[d.doc_type] = [])).push(d); });
    const keys = TYPE_ORDER.filter((k) => groups[k]).concat(Object.keys(groups).filter((k) => !TYPE_ORDER.includes(k)));
    catalog = keys.map((k) => `
      <h3 class="app-h3">${escapeHtml(TYPE_VI[k] || k)} <span class="app-badge">${groups[k].length}</span></h3>
      <div class="app-doclist">${groups[k].map(docRow).join("")}</div>`).join("");
  }

  const uploader = isMgr() ? `
    <h3 class="app-h3">Thêm tài liệu vào danh mục</h3>
    <div class="app-form" id="app-up">
      <div class="app-fg"><label class="app-label">Tên tài liệu <span class="app-req">*</span></label><input class="app-input" id="u-name"></div>
      <div class="app-fg"><label class="app-label">Mã tài liệu</label><input class="app-input" id="u-code" placeholder="VD: QT-09"></div>
      <div class="app-fg"><label class="app-label">Loại</label>
        <select class="app-input" id="u-type">
          <option value="Noi bo">Tài liệu nội bộ</option>
          <option value="Ben ngoai">Tài liệu bên ngoài (pháp luật, tiêu chuẩn)</option>
        </select></div>
      <div class="app-fg"><label class="app-label">Phiên bản</label><input class="app-input" id="u-ver" placeholder="vd: 01"></div>
      <div class="app-fg"><label class="app-label">Tệp (PDF/ảnh/Word)</label><input class="app-input" type="file" id="u-file"></div>
      <button class="app-btn app-btn-lg" id="u-go">Thêm vào danh mục</button>
      <div id="u-msg"></div>
    </div>` : "";

  container.innerHTML = `
    <h2 class="app-h2">Danh mục tài liệu</h2>
    ${catalog}
    ${uploader}`;

  if (isMgr()) container.querySelector("#u-go").addEventListener("click", () => doUpload(container));
}

function docRow(d) {
  const status = STATUS_VI[d.status] || d.status || "";
  const meta = [d.doc_code, d.version ? "v" + d.version : "", status].filter(Boolean).map(escapeHtml).join(" · ");
  const read = d.attachment
    ? `<a class="app-btn-sm" href="${escapeHtml(d.attachment)}" target="_blank" rel="noopener"><span class="material-symbols-outlined" style="font-size:18px">visibility</span>Đọc</a>`
    : '<span class="app-doc-noatt">chưa có tệp</span>';
  return `<div class="app-doc">
    <div class="app-doc-ic"><span class="material-symbols-outlined">description</span></div>
    <div class="app-doc-main">
      <div class="app-doc-name">${escapeHtml(d.doc_name || d.name)}</div>
      <div class="app-doc-meta">${meta}</div>
    </div>${read}</div>`;
}

async function doUpload(container) {
  const name = container.querySelector("#u-name").value.trim();
  const code = container.querySelector("#u-code").value.trim();
  const ver = container.querySelector("#u-ver").value.trim();
  const type = container.querySelector("#u-type").value;
  const fileEl = container.querySelector("#u-file");
  const msg = container.querySelector("#u-msg");
  if (!name) { msg.innerHTML = '<div class="app-alert app-alert-red">Cần tên tài liệu.</div>'; return; }
  const btn = container.querySelector("#u-go"); btn.disabled = true; msg.innerHTML = '<div class="app-alert">Đang lưu...</div>';
  try {
    let fileUrl = null;
    if (fileEl.files.length) { const up = await uploadFile(fileEl.files[0], 0); fileUrl = up.file_url; }
    await call("hg_food_safety.api.portal.create_document", {
      doc_name: name, doc_code: code, version: ver, attachment: fileUrl, doc_type: type });
    msg.innerHTML = '<div class="app-alert app-alert-ok">Đã thêm vào danh mục.</div>';
    setTimeout(() => render({ container }), 700);
  } catch (e) {
    btn.disabled = false;
    msg.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml((e.message || "").replace(/<[^>]+>/g, " "))}</div>`;
  }
}
