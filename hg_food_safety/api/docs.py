"""Doc Change Request: khi duyet -> ap dung phien ban moi vao Controlled Document."""
import frappe
from frappe.utils import nowdate


def apply_version(doc, method=None):
    """on_update_after_submit / workflow: neu trang thai 'Da duyet' -> cap nhat tai lieu.

    Idempotent: chi cap nhat khi co target_doc va new_version.
    """
    state = (getattr(doc, "workflow_state", "") or "")
    if state != "Da duyet" or not doc.target_doc:
        return
    cd = frappe.get_doc("Controlled Document", doc.target_doc)
    if doc.new_version:
        cd.version = doc.new_version
    cd.effective_date = nowdate()
    if doc.change_type == "Huy":
        cd.status = "Het hieu luc"
    cd.save(ignore_permissions=True)
