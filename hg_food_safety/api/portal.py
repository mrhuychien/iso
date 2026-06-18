"""API cho portal SPA: cong viec theo lich, tao ban ghi, tai lieu noi bo. Guard require_fs."""
import json
import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime
from hg_food_safety.api._guards import require_fs, is_manager, _guard

ALLOWED_CREATE = {
    "OPRP Monitoring Log", "Foreign Body Check Log", "Sanitation Log",
    "Water Control Log", "Sample Retention", "Rework Log", "Lab Test Result",
}
ALLOWED_LINK = {"Batch", "Item", "Employee"}
GROUP_ORDER = ["Hang ngay / Moi ca", "Dinh ky ngan", "Dinh ky 6 thang", "Hang nam", "Khi phat sinh"]

# Nhan hien thi co dau (DB luu ASCII de khop logic period_key / GROUP_ORDER).
GROUP_VI = {
    "Hang ngay / Moi ca": "Hằng ngày / Mỗi ca",
    "Dinh ky ngan": "Định kỳ ngắn",
    "Dinh ky 6 thang": "Định kỳ 6 tháng",
    "Hang nam": "Hằng năm",
    "Khi phat sinh": "Khi phát sinh",
}
FREQ_VI = {
    "Hang ngay": "Hằng ngày", "Moi ca": "Mỗi ca", "15 ngay": "15 ngày",
    "Hang thang": "Hằng tháng", "Hang quy": "Hằng quý", "6 thang": "6 tháng",
    "Hang nam": "Hằng năm", "Khi phat sinh": "Khi phát sinh",
}
TASK_VI = {
    "Giam sat OPRP theo ca": "Giám sát OPRP theo ca",
    "Kiem tra di vat / luoi sang / dau do": "Kiểm tra dị vật / lưới sàng / đầu dò",
    "Kiem tra thanh pham moi lo": "Kiểm tra thành phẩm mỗi lô",
    "Lay mau luu cuoi ngay": "Lấy mẫu lưu cuối ngày",
    "Nhat ky ve sinh dau/cuoi ca": "Nhật ký vệ sinh đầu/cuối ca",
    "Xa nuoc dau voi + cam quan nuoc": "Xả nước đầu vòi + cảm quan nước",
    "Ghi nhan hang tai che (rework)": "Ghi nhận hàng tái chế (rework)",
    "Diet ruoi muoi khu nha xuong": "Diệt ruồi muỗi khu nhà xưởng",
    "Kiem tra thiet bi PCCC": "Kiểm tra thiết bị PCCC",
    "Ve sinh dinh ky + diet con trung/chuot": "Vệ sinh định kỳ + diệt côn trùng/chuột",
    "Giam sat moi truong (swab be mat/khong khi)": "Giám sát môi trường (swab bề mặt/không khí)",
    "Bao duong dinh ky thiet bi san xuat": "Bảo dưỡng định kỳ thiết bị sản xuất",
    "Hieu chuan/kiem dinh thiet bi do": "Hiệu chuẩn/kiểm định thiết bị đo",
    "Ra soat danh muc thuy tinh - nhua gion": "Rà soát danh mục thủy tinh - nhựa giòn",
    "Kiem nghiem nuoc/san pham dinh ky": "Kiểm nghiệm nước/sản phẩm định kỳ",
    "Danh gia noi bo toan bo bo phan": "Đánh giá nội bộ toàn bộ bộ phận",
    "Tham tra he thong HACCP/OPRP": "Thẩm tra hệ thống HACCP/OPRP",
    "Xac dinh lai rui ro & co hoi": "Xác định lại rủi ro & cơ hội",
    "Tap huan kien thuc VSATTP": "Tập huấn kiến thức VSATTP",
    "Kham suc khoe dinh ky cong nhan": "Khám sức khỏe định kỳ công nhân",
    "Dien tap tinh huong khan cap": "Diễn tập tình huống khẩn cấp",
    "Dien tap thu hoi (mock recall)": "Diễn tập thu hồi (mock recall)",
    "Danh gia phong ve thuc pham (TACCP/VACCP)": "Đánh giá phòng vệ thực phẩm (TACCP/VACCP)",
    "Tham dinh han su dung (shelf-life)": "Thẩm định hạn sử dụng (shelf-life)",
    "Danh gia & duyet nha cung cap": "Đánh giá & duyệt nhà cung cấp",
    "Kiem tra chat luong hang nhap": "Kiểm tra chất lượng hàng nhập",
    "Thu hoi san pham mat an toan": "Thu hồi sản phẩm mất an toàn",
}


def _ensure_today():
    """Tu seed ATTP Task (neu trong) + sinh log den ky -> list luon co viec hien."""
    try:
        if not frappe.db.count("ATTP Task"):
            from hg_food_safety.setup.install import ensure_tasks
            ensure_tasks()
        from hg_food_safety.schedule import generate_task_logs
        generate_task_logs()
    except Exception:
        frappe.log_error(title="today_tasks ensure")


@frappe.whitelist()
def today_tasks() -> dict:
    """Cong viec dang cho/tre (checklist theo lich cong viec ATTP), gom theo nhom."""
    require_fs()
    _ensure_today()
    logs = frappe.get_all("ATTP Task Log",
        filters={"status": ["in", ["Cho lam", "Tre"]]},
        fields=["name", "task", "title", "task_group", "frequency", "status", "period_date"],
        order_by="period_date asc")
    groups = {}
    for l in logs:
        form = frappe.db.get_value("ATTP Task", l.task, "linked_form")
        l["linked_form"] = form or ""
        l["title"] = TASK_VI.get(l.title, l.title)
        l["frequency"] = FREQ_VI.get(l.frequency, l.frequency)
        groups.setdefault(l.task_group or "Khac", []).append(l)
    ordered = [{"group": GROUP_VI.get(g, g), "tasks": groups[g]} for g in GROUP_ORDER if g in groups]
    for g in groups:
        if g not in GROUP_ORDER:
            ordered.append({"group": GROUP_VI.get(g, g), "tasks": groups[g]})
    done_today = frappe.db.count("ATTP Task Log", {"status": "Da lam", "done_on": [">=", nowdate() + " 00:00:00"]})
    return {
        "date": nowdate(),
        "is_manager": is_manager(),
        "groups": ordered,
        "open_count": len(logs),
        "overdue_count": sum(1 for l in logs if l.status == "Tre"),
        "done_today": done_today,
        "batches_on_hold": frappe.db.count("Batch", {"custom_qc_hold": 1}) if frappe.db.has_column("Batch", "custom_qc_hold") else 0,
    }


@frappe.whitelist()
def mark_task_done(log: str, note: str = None) -> dict:
    """Danh dau mot cong viec da lam (cho cong viec khong gan bieu mau)."""
    require_fs()
    doc = frappe.get_doc("ATTP Task Log", log)
    doc.status = "Da lam"
    doc.done_by = frappe.session.user
    doc.done_on = now_datetime()
    if note:
        doc.note = note
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def search_link(doctype: str, txt: str = "") -> list:
    """Tim ban ghi cho truong Link tren portal."""
    require_fs()
    if doctype not in ALLOWED_LINK:
        frappe.throw(_("Khong duoc phep tra cuu DocType nay"), frappe.PermissionError)
    txt = (txt or "").strip()
    fields = ["name"] + (["employee_name"] if doctype == "Employee" else (["item_name"] if doctype == "Item" else []))
    rows = frappe.get_all(doctype, or_filters={"name": ["like", f"%{txt}%"]} if txt else None,
                          fields=fields, limit_page_length=12, order_by="modified desc")
    out = []
    for r in rows:
        label = r.get("employee_name") or r.get("item_name") or r["name"]
        out.append({"value": r["name"], "label": f"{r['name']} - {label}" if label != r["name"] else r["name"]})
    return out


@frappe.whitelist()
def create_record(doctype: str, payload, submit: int = 0) -> dict:
    """Tao ban ghi tac nghiep tu portal (permission do Frappe kiem). Tu danh dau cong viec lien quan."""
    require_fs()
    if doctype not in ALLOWED_CREATE:
        frappe.throw(_("Khong duoc phep tao DocType nay tu portal"), frappe.PermissionError)
    data = json.loads(payload) if isinstance(payload, str) else (payload or {})
    meta = frappe.get_meta(doctype)
    valid = {df.fieldname for df in meta.fields}
    doc = frappe.new_doc(doctype)
    for k, v in data.items():
        if k in valid:
            doc.set(k, v)
    doc.insert()
    if int(submit or 0) and meta.is_submittable:
        doc.submit()
    _auto_complete_task(doctype, doc.name)
    return {"name": doc.name, "docstatus": doc.docstatus}


def _auto_complete_task(doctype, docname):
    """Danh dau log cong viec dang mo co linked_doctype trung -> Da lam."""
    try:
        logs = frappe.get_all("ATTP Task Log",
            filters={"status": ["in", ["Cho lam", "Tre"]], "reference_name": ["is", "not set"]},
            fields=["name", "task"], order_by="period_date desc")
        for lg in logs:
            if frappe.db.get_value("ATTP Task", lg.task, "linked_doctype") == doctype:
                frappe.db.set_value("ATTP Task Log", lg.name, {
                    "status": "Da lam", "done_by": frappe.session.user,
                    "done_on": now_datetime(), "reference_doctype": doctype, "reference_name": docname})
                break
    except Exception:
        frappe.log_error(title="auto_complete_task")


# ─────────────── Tai lieu noi bo ───────────────
DOC_TYPES = ("Noi bo", "Ben ngoai")
DOC_STATUS = ("Hieu luc", "Da thay the", "Het hieu luc")
DOC_CATS = ("Chinh sach - Muc tieu", "So tay - PRP/SSOP", "Ke hoach (HACCP/OPRP/KN/SL)",
            "Quy trinh (QT)", "Quy dinh (QD)", "Bieu mau - Ho so (BM)",
            "Danh muc - Dinh muc", "Tai lieu ben ngoai")


@frappe.whitelist()
def documents() -> list:
    """Danh muc tai lieu kiem soat (noi bo + ben ngoai), kem so lan cap nhat. Vai tro FS deu xem duoc."""
    require_fs()
    rows = frappe.get_all("Controlled Document",
        fields=["name", "doc_name", "doc_code", "doc_category", "doc_type", "version", "status",
                "attachment", "summary", "location", "retention", "effective_date", "modified"],
        order_by="doc_code asc, modified desc")
    for r in rows:
        r["change_count"] = frappe.db.count("Controlled Document Change", {"parent": r["name"]})
    return rows


@frappe.whitelist()
def document_history(name: str) -> list:
    """Lich su cap nhat cua mot tai lieu (moi -> cu)."""
    require_fs()
    return frappe.get_all("Controlled Document Change",
        filters={"parent": name, "parenttype": "Controlled Document"},
        fields=["changed_on", "changed_by", "action", "version", "note"],
        order_by="changed_on desc, idx desc")


def _add_change(doc, action, note=None):
    doc.append("change_log", {
        "changed_on": now_datetime(), "changed_by": frappe.session.user,
        "action": action, "version": doc.version or "", "note": note or "",
    })


@frappe.whitelist()
def create_document(doc_name: str, doc_code: str = None, doc_category: str = None,
                    doc_type: str = "Noi bo", version: str = None, status: str = "Hieu luc",
                    attachment: str = None, summary: str = None, location: str = None,
                    retention: str = None) -> dict:
    """Them tai lieu vao danh muc (chi quan ly QA). attachment = file_url da upload."""
    _guard()
    doc = frappe.get_doc({
        "doctype": "Controlled Document", "doc_name": doc_name, "doc_code": doc_code,
        "doc_category": doc_category if doc_category in DOC_CATS else None,
        "doc_type": doc_type if doc_type in DOC_TYPES else "Noi bo",
        "version": version, "status": status if status in DOC_STATUS else "Hieu luc",
        "attachment": attachment, "summary": summary, "location": location, "retention": retention,
    })
    _add_change(doc, "Tao moi")
    doc.insert()
    return {"name": doc.name}


@frappe.whitelist()
def update_document(name: str, doc_name: str = None, doc_code: str = None, doc_category: str = None,
                    doc_type: str = None, version: str = None, status: str = None,
                    attachment: str = None, summary: str = None, location: str = None,
                    retention: str = None, note: str = None) -> dict:
    """Cap nhat tai lieu trong danh muc (chi quan ly QA) + ghi log thay doi cac truong."""
    _guard()
    doc = frappe.get_doc("Controlled Document", name)
    changes = []
    fields = {
        "doc_name": doc_name, "doc_code": doc_code, "version": version,
        "summary": summary, "location": location, "retention": retention, "attachment": attachment,
    }
    if doc_category in DOC_CATS:
        fields["doc_category"] = doc_category
    if doc_type in DOC_TYPES:
        fields["doc_type"] = doc_type
    if status in DOC_STATUS:
        fields["status"] = status
    for f, v in fields.items():
        if v is not None and (doc.get(f) or "") != v:
            doc.set(f, v)
            changes.append(frappe.unscrub(f))
    summary_txt = ", ".join(changes) if changes else "Khong doi truong"
    _add_change(doc, "Cap nhat", (note + " — " if note else "") + "Thay doi: " + summary_txt)
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "changed": changes}
