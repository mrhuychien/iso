"""API cho portal SPA: viec hom nay, tao ban ghi, tim Link. Guard bang require_fs."""
import json
import frappe
from frappe import _
from frappe.utils import nowdate
from hg_food_safety.api._guards import require_fs, is_manager

# Chi cho phep tao tu portal cac DocType tac nghiep hang ngay (an toan).
ALLOWED_CREATE = {
    "OPRP Monitoring Log", "Foreign Body Check Log", "Sanitation Log",
    "Water Control Log", "Sample Retention", "Rework Log", "Lab Test Result",
}
# Link duoc phep tra cuu tu portal.
ALLOWED_LINK = {"Batch", "Item", "Employee"}


@frappe.whitelist()
def my_today() -> dict:
    """Tom tat viec hom nay cho nguoi dang nhap (KCS/QA)."""
    require_fs()
    today = nowdate()
    return {
        "user": frappe.session.user,
        "is_manager": is_manager(),
        "date": today,
        "done": {
            "oprp": frappe.db.count("OPRP Monitoring Log", {"log_date": today, "owner": frappe.session.user}),
            "foreign_body": frappe.db.count("Foreign Body Check Log", {"log_date": today, "owner": frappe.session.user}),
            "sanitation": frappe.db.count("Sanitation Log", {"log_date": today, "owner": frappe.session.user}),
            "water": frappe.db.count("Water Control Log", {"log_date": today, "owner": frappe.session.user}),
        },
        "batches_on_hold": frappe.db.count("Batch", {"custom_qc_hold": 1}) if frappe.db.has_column("Batch", "custom_qc_hold") else 0,
    }


@frappe.whitelist()
def search_link(doctype: str, txt: str = "") -> list:
    """Tim ban ghi cho truong Link tren portal. Chi cho phep mot so DocType."""
    require_fs()
    if doctype not in ALLOWED_LINK:
        frappe.throw(_("Khong duoc phep tra cuu DocType nay"), frappe.PermissionError)
    txt = (txt or "").strip()
    fields = ["name"]
    if doctype == "Employee":
        fields.append("employee_name")
    if doctype == "Item":
        fields.append("item_name")
    rows = frappe.get_all(
        doctype,
        or_filters={"name": ["like", f"%{txt}%"]} if txt else None,
        fields=fields, limit_page_length=12, order_by="modified desc",
    )
    out = []
    for r in rows:
        label = r.get("employee_name") or r.get("item_name") or r["name"]
        out.append({"value": r["name"], "label": f"{r['name']} - {label}" if label != r["name"] else r["name"]})
    return out


@frappe.whitelist()
def create_record(doctype: str, payload, submit: int = 0) -> dict:
    """Tao mot ban ghi tac nghiep tu portal. Quyen do DocType permission kiem (khong bypass).

    - Chi cho phep DocType trong ALLOWED_CREATE.
    - Chi set field hop le theo meta (gom child table).
    - submit=1 + DocType submittable -> submit luon.
    """
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
    doc.insert()  # permission-checked: user phai co quyen create
    if int(submit or 0) and meta.is_submittable:
        doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}
