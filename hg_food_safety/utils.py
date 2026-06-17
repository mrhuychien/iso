"""Ham dung chung cho he thong ATTP: co lap lo + mo Non Conformance."""
import frappe
from frappe import _


def hold_batch(batch_no: str, reason: str):
    """Dat co lap (QC Hold) cho mot Batch. Idempotent."""
    if not batch_no or not frappe.db.exists("Batch", batch_no):
        return
    frappe.db.set_value("Batch", batch_no, {
        "custom_qc_status": "Co lap",
        "custom_qc_hold": 1,
    })
    frappe.msgprint(_("Lo {0} da bi CO LAP: {1}").format(batch_no, reason),
                    indicator="red", alert=True)


def open_non_conformance(subject: str, details: str, ref_doctype: str = None, ref_name: str = None):
    """Tao Non Conformance (module Quality cua ERPNext) neu DocType ton tai. Idempotent."""
    if not frappe.db.exists("DocType", "Non Conformance"):
        return None
    # Tranh trung: 1 NC mo cho cung subject trong ngay
    existing = frappe.db.exists("Non Conformance", {"subject": subject, "status": "Open"})
    if existing:
        return existing
    detail_text = details
    if ref_doctype and ref_name:
        detail_text = f"{details}\nNguon: {ref_doctype} {ref_name}"
    nc = frappe.get_doc({
        "doctype": "Non Conformance",
        "subject": subject,
        "status": "Open",
        "details": detail_text,
    })
    nc.insert(ignore_permissions=True)
    return nc.name
