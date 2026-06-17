"""Khoi tao trang thai ATTP cho Batch khi san xuat (Stock Entry = Manufacture)."""
import frappe


def init_finished_batch(doc, method=None):
    """on_submit Stock Entry: voi cac batch moi xuat hien o muc Manufacture,
    dat trang thai ATTP mac dinh = 'Dang san xuat' neu chua co."""
    if getattr(doc, "purpose", None) != "Manufacture":
        return
    for item in doc.items:
        batch_no = getattr(item, "batch_no", None)
        if not batch_no:
            continue
        current = frappe.db.get_value("Batch", batch_no, "custom_qc_status")
        if not current:
            frappe.db.set_value("Batch", batch_no, "custom_qc_status", "Dang san xuat")
