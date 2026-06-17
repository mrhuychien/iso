"""Truy xuat theo lo (ma lo): tra ve toan bo ho so ATTP lien quan."""
import frappe
from frappe import _


@frappe.whitelist()
def by_batch(batch_no: str) -> dict:
    """Tra ve cac ban ghi ATTP gan voi mot Batch (cho man hinh truy xuat/thu hoi).

    Permission: yeu cau quyen doc Batch.
    """
    if not frappe.has_permission("Batch", doc=batch_no, ptype="read"):
        frappe.throw(_("Khong co quyen doc lo nay"), frappe.PermissionError)

    def q(doctype, extra_fields=None):
        if not frappe.db.exists("DocType", doctype):
            return []
        fields = ["name", "creation"] + (extra_fields or [])
        return frappe.get_all(doctype, filters={"batch_no": batch_no},
                              fields=fields, order_by="creation asc")

    return {
        "batch_no": batch_no,
        "batch_status": frappe.db.get_value("Batch", batch_no, "custom_qc_status"),
        "oprp": q("OPRP Monitoring Log", ["log_date", "shift", "has_deviation"]),
        "foreign_body": q("Foreign Body Check Log", ["log_date", "status"]),
        "finished_inspection": q("Quality Inspection", ["item_code", "status"]) if frappe.db.has_column("Quality Inspection", "batch_no") else [],
        "sample_retention": q("Sample Retention", ["retention_date", "keep_until"]),
    }
