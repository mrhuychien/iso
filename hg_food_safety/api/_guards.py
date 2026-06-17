"""Permission guards dung chung cho moi whitelisted method (kieu NPP).

- _guard(): chi quan ly (FS QA Manager / System Manager).
- require_fs(): bat ky vai tro ATTP (QC hoac QA) - cho man hinh ghi/truy xuat.
Quyen THAT van do DocType permission kiem; day la lop guard dau method.
"""
import frappe
from frappe import _

MANAGER_ROLES = {"FS QA Manager", "System Manager"}
FS_ROLES = {"FS QC", "FS QA Manager", "System Manager"}


def is_manager() -> bool:
    return bool(MANAGER_ROLES & set(frappe.get_roles()))


def _guard():
    """Chan neu khong phai quan ly ATTP."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Yeu cau dang nhap"), frappe.PermissionError)
    if not is_manager():
        frappe.throw(_("Chi quan ly ATTP (FS QA Manager) duoc xem muc nay"), frappe.PermissionError)


def require_fs():
    """Chan neu khong co vai tro ATTP nao."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Yeu cau dang nhap"), frappe.PermissionError)
    if not (FS_ROLES & set(frappe.get_roles())):
        frappe.throw(_("Khong co quyen truy cap he thong ATTP"), frappe.PermissionError)
