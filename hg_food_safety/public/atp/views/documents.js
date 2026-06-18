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
const APPR_VI = { "Ban nhap": "Bản nháp", "Cho duyet": "Chờ duyệt", "Da duyet": "Đã duyệt" };
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
  if (isMgr()) container.querySelector("#a-go").addEventListener("click", () => doAdd(container));
}

function docRow(d) {
  const status = STATUS_VI[d.status] || d.status || "";
  const meta = [d.doc_code, d.version ? "v" + d.version : "", status, d.location]
    .filter(Boolean).map(escapeHtml).join(" · ");
  const pending = d.approval_status === "Cho duyet"
    ? '<span class="app-chip app-chip-warn">Chờ duyệt</span>' : "";
  const read = d.attachment
    ? `<a class="app-btn-sm" href="${escapeHtml(d.attachment)}" target="_blank" rel="noopener" title="Mở tệp" onclick="event.stopPropagation()"><span class="material-symbols-outlined" style="font-size:18px">visibility</span></a>`
    : "";
  return `<div class="app-doc app-doc-click" data-view="${escapeHtml(d.name)}" role="button" tabindex="0">
    <div class="app-doc-ic"><span class="material-symbols-outlined">description</span></div>
    <div class="app-doc-main">
      <div class="app-doc-name">${escapeHtml(d.doc_name || d.name)}</div>
      <div class="app-doc-meta">${meta} ${pending}</div>
    </div>
    <div class="app-doc-act">${read}<span class="material-symbols-outlined app-doc-chev">chevron_right</span></div></div>`;
}

/* ---------- Sanitize HTML noi dung (tin cay han che) ---------- */
function sanitize(html) {
  const t = document.createElement("div");
  t.innerHTML = html || "";
  t.querySelectorAll("script,style,iframe,object,embed,link,meta,form").forEach((n) => n.remove());
  t.querySelectorAll("*").forEach((n) => {
    [...n.attributes].forEach((a) => {
      if (/^on/i.test(a.name) || (/^(href|src)$/i.test(a.name) && /^\s*javascript:/i.test(a.value)))
        n.removeAttribute(a.name);
    });
  });
  return t.innerHTML;
}

/* ---------- Modal (gan vao .app-root de ke thua bien CSS) ---------- */
function modal(title, bodyHtml, wide) {
  const host = document.querySelector(".app-root") || document.body;
  const ov = document.createElement("div");
  ov.className = "app-modal-ov";
  ov.innerHTML = `<div class="app-modal${wide ? " app-modal-wide" : ""}" role="dialog">
    <div class="app-modal-head"><span>${escapeHtml(title)}</span><button class="app-modal-x" aria-label="Đóng">×</button></div>
    <div class="app-modal-body">${bodyHtml}</div></div>`;
  host.appendChild(ov);
  const close = () => ov.remove();
  ov.addEventListener("click", (e) => { if (e.target === ov) close(); });
  ov.querySelector(".app-modal-x").addEventListener("click", close);
  return { ov, close };
}

function kv(label, value) {
  if (!value) return "";
  return `<div class="app-kv"><span class="app-kv-l">${escapeHtml(label)}</span><span class="app-kv-v">${escapeHtml(value)}</span></div>`;
}

async function openDetail(name, container) {
  const { ov, close } = modal("Chi tiết tài liệu", '<div class="app-muted">Đang tải...</div>', true);
  const body = ov.querySelector(".app-modal-body");
  let d;
  try { d = await call("hg_food_safety.api.portal.document_get", { name }); }
  catch (e) { body.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }

  const appr = d.approval_status || "Da duyet";
  const apprClass = appr === "Da duyet" ? "ok" : (appr === "Cho duyet" ? "warn" : "muted");
  const tags = [
    d.doc_category ? `<span class="app-tag">${escapeHtml(CAT_VI[d.doc_category] || d.doc_category)}</span>` : "",
    `<span class="app-tag">${escapeHtml(TYPE_VI[d.doc_type] || d.doc_type || "")}</span>`,
    `<span class="app-tag app-tag-${d.status === "Hieu luc" ? "ok" : "muted"}">${escapeHtml(STATUS_VI[d.status] || d.status || "")}</span>`,
    `<span class="app-tag app-tag-${apprClass}">${escapeHtml(APPR_VI[appr] || appr)}</span>`,
  ].join("");

  const content = d.content
    ? `<div class="app-prose">${sanitize(d.content)}</div>`
    : '<div class="app-alert">Tài liệu chưa có nội dung soạn thảo.</div>';

  let approveArea = "";
  if (appr === "Da duyet" && d.signed_pdf) {
    approveArea = `<div class="app-approve app-approve-ok">
      <span class="material-symbols-outlined">verified</span>
      <div>Đã phê duyệt${d.approved_by ? " bởi " + escapeHtml(d.approved_by) : ""}${d.approved_on ? " · " + escapeHtml(d.approved_on.replace("T", " ").slice(0, 16)) : ""}
        <a class="app-link-strong" href="${escapeHtml(d.signed_pdf)}" target="_blank" rel="noopener">Xem bản PDF đã ký →</a></div></div>`;
  } else if (appr === "Cho duyet") {
    approveArea = isMgr()
      ? `<div class="app-approve app-approve-warn">
          <div class="app-approve-h"><span class="material-symbols-outlined">pending</span> Bản sửa đang chờ phê duyệt. Tải bản PDF có chữ ký giám đốc để phê duyệt:</div>
          <input type="file" id="ap-file" accept="application/pdf,image/*" class="app-input">
          <button class="app-btn" id="ap-go"><span class="material-symbols-outlined" style="font-size:19px">verified</span>Phê duyệt & lưu bản ký</button>
          <div id="ap-msg"></div></div>`
      : `<div class="app-approve app-approve-warn"><span class="material-symbols-outlined">pending</span> Bản sửa đang chờ giám đốc phê duyệt.</div>`;
  }

  body.innerHTML = `
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
    ${d.summary ? `<div class="app-detail-sum"><div class="app-kv-l" style="margin-bottom:6px">Tóm tắt</div>${escapeHtml(d.summary)}</div>` : ""}
    <div class="app-h3" style="margin:20px 0 10px">Nội dung tài liệu</div>
    ${content}
    ${approveArea}
    <div class="app-detail-act">
      ${d.attachment ? `<a class="app-btn-sm app-btn-ghost" href="${escapeHtml(d.attachment)}" target="_blank" rel="noopener"><span class="material-symbols-outlined" style="font-size:18px">attach_file</span>Tệp kèm</a>` : ""}
      <button class="app-btn-sm app-btn-ghost" data-d-hist><span class="material-symbols-outlined" style="font-size:18px">history</span>Lịch sử (${escapeHtml(String(d.change_count || 0))})</button>
      ${isMgr() ? '<button class="app-btn app-btn-sm-solid" data-d-edit><span class="material-symbols-outlined" style="font-size:18px">edit</span>Sửa nội dung</button>' : ""}
    </div>`;

  ov.querySelector("[data-d-hist]").addEventListener("click", () => openHistory(name));
  const eb = ov.querySelector("[data-d-edit]");
  if (eb) eb.addEventListener("click", () => { close(); openEditor(name, container); });
  const apGo = ov.querySelector("#ap-go");
  if (apGo) apGo.addEventListener("click", () => doApprove(name, ov, container, close));
}

async function doApprove(name, ov, container, close) {
  const fileEl = ov.querySelector("#ap-file");
  const msg = ov.querySelector("#ap-msg");
  if (!fileEl.files.length) { msg.innerHTML = '<div class="app-alert app-alert-red">Cần chọn bản PDF có chữ ký giám đốc.</div>'; return; }
  const btn = ov.querySelector("#ap-go"); btn.disabled = true;
  msg.innerHTML = '<div class="app-alert">Đang tải lên & phê duyệt...</div>';
  try {
    const up = await uploadFile(fileEl.files[0], 0);
    await call("hg_food_safety.api.portal.approve_document", { name, signed_pdf: up.file_url });
    close();
    await render({ container });
    openDetail(name, container);
  } catch (e) {
    btn.disabled = false;
    msg.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml((e.message || "").replace(/<[^>]+>/g, " "))}</div>`;
  }
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

/* ---------- WYSIWYG (no-build, contenteditable) ---------- */
function wysiwyg(initialHtml) {
  const wrap = document.createElement("div");
  wrap.className = "app-rte";
  wrap.innerHTML = `
    <div class="app-rte-tb">
      <button type="button" data-cmd="bold" title="Đậm"><b>B</b></button>
      <button type="button" data-cmd="italic" title="Nghiêng"><i>I</i></button>
      <button type="button" data-cmd="underline" title="Gạch chân"><u>U</u></button>
      <span class="app-rte-sep"></span>
      <button type="button" data-cmd="formatBlock" data-val="H2" title="Tiêu đề lớn">H2</button>
      <button type="button" data-cmd="formatBlock" data-val="H3" title="Tiêu đề nhỏ">H3</button>
      <button type="button" data-cmd="formatBlock" data-val="P" title="Đoạn văn">¶</button>
      <span class="app-rte-sep"></span>
      <button type="button" data-cmd="insertUnorderedList" title="Danh sách">•</button>
      <button type="button" data-cmd="insertOrderedList" title="Danh sách số">1.</button>
      <span class="app-rte-sep"></span>
      <button type="button" data-cmd="removeFormat" title="Xoá định dạng">✕</button>
    </div>
    <div class="app-rte-area" contenteditable="true"></div>`;
  const area = wrap.querySelector(".app-rte-area");
  area.innerHTML = initialHtml || "<p></p>";
  wrap.querySelectorAll(".app-rte-tb button").forEach((b) =>
    b.addEventListener("click", (e) => {
      e.preventDefault();
      area.focus();
      document.execCommand(b.dataset.cmd, false, b.dataset.val || null);
    }));
  return { wrap, get: () => area.innerHTML };
}

async function openEditor(name, container) {
  const { ov, close } = modal("Sửa tài liệu", '<div class="app-muted">Đang tải...</div>', true);
  const body = ov.querySelector(".app-modal-body");
  let d;
  try { d = await call("hg_food_safety.api.portal.document_get", { name }); }
  catch (e) { body.innerHTML = `<div class="app-alert app-alert-red">${escapeHtml(e.message)}</div>`; return; }

  body.innerHTML = `
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
      <div class="app-fg"><label class="app-label">Nội dung tài liệu (soạn thảo)</label><div id="e-rte-host"></div></div>
      <div class="app-fg"><label class="app-label">Tóm tắt</label><textarea class="app-input" id="e-sum" rows="2">${escapeHtml(d.summary || "")}</textarea></div>
      <div class="app-fg"><label class="app-label">Lý do / ghi chú cập nhật</label><input class="app-input" id="e-note" placeholder="VD: cập nhật theo VBHN 09/2024"></div>
      <div class="app-alert" style="margin:0">Sau khi lưu, tài liệu chuyển trạng thái <b>Chờ duyệt</b>. Giám đốc/QA phê duyệt bằng cách tải bản PDF có chữ ký.</div>
      <button class="app-btn app-btn-lg" id="e-save">Lưu bản sửa</button>
      <div id="e-msg"></div>
    </div>`;
  const rte = wysiwyg(d.content);
  body.querySelector("#e-rte-host").appendChild(rte.wrap);

  ov.querySelector("#e-save").addEventListener("click", async () => {
    const nm = (ov.querySelector("#e-name").value || "").trim();
    const msg = ov.querySelector("#e-msg");
    if (!nm) { msg.innerHTML = '<div class="app-alert app-alert-red">Cần tên tài liệu.</div>'; return; }
    const btn = ov.querySelector("#e-save"); btn.disabled = true;
    msg.innerHTML = '<div class="app-alert">Đang lưu...</div>';
    try {
      await call("hg_food_safety.api.portal.update_document", {
        name, doc_name: nm, doc_code: ov.querySelector("#e-code").value.trim(),
        doc_category: ov.querySelector("#e-cat").value, doc_type: ov.querySelector("#e-type").value,
        version: ov.querySelector("#e-ver").value.trim(), status: ov.querySelector("#e-status").value,
        summary: ov.querySelector("#e-sum").value.trim(), content: rte.get(),
        note: ov.querySelector("#e-note").value.trim(),
      });
      close();
      await render({ container });
      openDetail(name, container);
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
