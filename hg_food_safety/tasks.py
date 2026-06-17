"""Scheduled tasks cho he thong ATTP. Tat ca idempotent, chi tao Notification/ToDo."""
import frappe
from frappe.utils import nowdate, add_days, getdate


def remind_sample_disposal():
    """Nhac huy mau luu khi den han (keep_until <= hom nay, chua huy)."""
    rows = frappe.get_all(
        "Sample Retention",
        filters={"keep_until": ("<=", nowdate()), "disposed_on": ("is", "not set")},
        fields=["name", "item", "batch_no", "keep_until"],
    )
    for r in rows:
        _notify_qa(
            subject=f"Mau luu den han huy: {r.name} (lo {r.batch_no})",
            doctype="Sample Retention",
            docname=r.name,
        )


def remind_calibration_due():
    """Nhac hieu chuan/kiem dinh thiet bi do truoc han 30 ngay."""
    if not frappe.db.exists("DocType", "Calibration Record"):
        return
    threshold = add_days(nowdate(), 30)
    rows = frappe.get_all(
        "Calibration Record",
        filters={"next_due": ("between", [nowdate(), threshold])},
        fields=["name", "asset", "next_due"],
    )
    for r in rows:
        _notify_qa(
            subject=f"Thiet bi {r.asset} sap den han hieu chuan ({r.next_due})",
            doctype="Calibration Record",
            docname=r.name,
        )


def remind_lab_test_due():
    """Placeholder: nhac kiem nghiem dinh ky (mo rong khi co Lab Test Result)."""
    return


def _notify_qa(subject, doctype, docname):
    """Tao ToDo cho moi user co role FS QA Manager. Tranh trung trong ngay."""
    qa_users = frappe.get_all(
        "Has Role", filters={"role": "FS QA Manager", "parenttype": "User"},
        fields=["parent"], distinct=True,
    )
    for u in qa_users:
        exists = frappe.db.exists("ToDo", {
            "reference_type": doctype, "reference_name": docname,
            "allocated_to": u.parent, "status": "Open",
        })
        if not exists:
            frappe.get_doc({
                "doctype": "ToDo", "allocated_to": u.parent,
                "reference_type": doctype, "reference_name": docname,
                "description": subject, "date": nowdate(),
            }).insert(ignore_permissions=True)
