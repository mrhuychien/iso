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
        groups.setdefault(l.task_group or "Khac", []).append(l)
    ordered = [{"group": g, "tasks": groups[g]} for g in GROUP_ORDER if g in groups]
    for g in groups:
        if g not in GROUP_ORDER:
            ordered.append({"group": g, "tasks": groups[g]})
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
@frappe.whitelist()
def documents() -> list:
    """Danh sach tai lieu kiem soat (doc online). Moi vai tro FS deu xem duoc."""
    require_fs()
    return frappe.get_all("Controlled Document",
        filters={"doc_type": "Noi bo"},
        fields=["name", "doc_name", "doc_code", "version", "status", "attachment", "summary", "modified"],
        order_by="doc_code asc, modified desc")


@frappe.whitelist()
def create_document(doc_name: str, doc_code: str = None, version: str = None,
                    attachment: str = None, summary: str = None) -> dict:
    """Tao tai lieu noi bo (chi quan ly QA). attachment = file_url da upload."""
    _guard()
    doc = frappe.get_doc({
        "doctype": "Controlled Document", "doc_name": doc_name, "doc_code": doc_code,
        "doc_type": "Noi bo", "version": version, "status": "Hieu luc",
        "attachment": attachment, "summary": summary,
    })
    doc.insert()
    return {"name": doc.name}
