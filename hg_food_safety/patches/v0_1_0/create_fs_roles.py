import frappe


def execute():
    """Tao Role FS QC va FS QA Manager neu chua co. Idempotent."""
    for role_name in ("FS QC", "FS QA Manager"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1,
            }).insert(ignore_permissions=True)
