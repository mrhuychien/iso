import { call, uploadFile } from "../lib/api.js";
import { escapeHtml } from "../lib/format.js";

const isMgr = () => !!(window.FS_CONTEXT && window.FS_CONTEXT.isManager);

export async function render({ container }) {
  container.innerHTML = '<div class="app-card app-muted">Đang tải tài liệu...</div>';
  let docs = [];
  try { docs = await call("hg_food_safety.api.portal.documents"); }
  catch (e) { container.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }

  const list = docs.length ? docs.map((d) => `
    <div class="app-doc">
      <div class="app-doc-ic"><span class="material-symbols-outlined">description</span></div>
      <div class="app-doc-main">
        <div class="app-doc-name">${escapeHtml(d.doc_name || d.name)}</div>
        <div class="app-doc-meta">${escapeHtml(d.doc_code || "")}${d.version ? " · v" + escapeHtml(d.version) : ""} · ${escapeHtml(d.status || "")}</div>
      </div>
      ${d.attachment ? `<a class="app-btn-sm" href="${escapeHtml(d.attachment)}" target="_blank" rel="noopener">Đọc</a>` : '<span class="app-doc-noatt">chưa có tệp</span>'}
    </div>`).join("") : '<div class="app-alert">Chưa có tài liệu nội bộ.</div>';

  const uploader = isMgr() ? `
    <h3 class="app-h3">Tải tài liệu lên</h3>
    <div class="app-form" id="app-up">
      <div class="app-fg"><label class="app-label">Tên tài liệu <span class="app-req">*</span></label><input class="app-input" id="u-name"></div>
      <div class="app-fg"><label class="app-label">Mã tài liệu</label><input class="app-input" id="u-code"></div>
      <div class="app-fg"><label class="app-label">Phiên bản</label><input class="app-input" id="u-ver" placeholder="vd: 01"></div>
      <div class="app-fg"><label class="app-label">Tệp (PDF/ảnh/Word) <span class="app-req">*</span></label><input class="app-input" type="file" id="u-file"></div>
      <button class="app-btn app-btn-lg" id="u-go">Tải lên</button>
      <div id="u-msg"></div>
    </div>` : "";

  container.innerHTML = `
    <h2 class="app-h2">Tài liệu nội bộ</h2>
    <div class="app-doclist">${list}</div>
    ${uploader}`;

  if (isMgr()) container.querySelector("#u-go").addEventListener("click", () => doUpload(container));
}

async function doUpload(container) {
  const name = container.querySelector("#u-name").value.trim();
  const code = container.querySelector("#u-code").value.trim();
  const ver = container.querySelector("#u-ver").value.trim();
  const fileEl = container.querySelector("#u-file");
  const msg = container.querySelector("#u-msg");
  if (!name || !fileEl.files.length) { msg.innerHTML = '<div class="app-alert app-alert-red">Cần tên tài liệu và tệp.</div>'; return; }
  const btn = container.querySelector("#u-go"); btn.disabled = true; msg.innerHTML = '<div class="app-alert">Đang tải lên...</div>';
  try {
    const up = await uploadFile(fileEl.files[0], 0);
    await call("hg_food_safety.api.portal.create_document", {
      doc_name: name, doc_code: code, version: ver, attachment: up.file_url });
    msg.innerHTML = '<div class="app-alert app-alert-ok">Đã tải lên.</div>';
    setTimeout(() => render({ container }), 700);
  } catch (e) {
    btn.disabled = false;
    msg.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml((e.message || "").replace(/<[^>]+>/g, " "))}</div>`;
  }
}
