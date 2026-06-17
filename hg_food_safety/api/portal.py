"""API cho portal SPA: viec hom nay + truy xuat. Guard bang require_fs."""
import frappe
from frappe.utils import nowdate
from hg_food_safety.api._guards import require_fs, is_manager


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
        "batches_on_hold": frappe.db.count("Batch", {"custom_qc_hold": 1}),
    }
