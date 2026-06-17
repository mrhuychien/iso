"""Sinh log cong viec ATTP theo lich (tan suat) + danh dau tre.

Goi hang ngay tu scheduler. period_key bao dam idempotent (1 log/ky/cong viec).
"""
import frappe
from frappe.utils import nowdate, getdate


def period_key(freq, d=None):
    d = getdate(d or nowdate())
    if freq in ("Hang ngay", "Moi ca"):
        return d.isoformat()
    if freq == "15 ngay":
        return f"{d.year}-B{(d.timetuple().tm_yday - 1) // 15}"
    if freq == "Hang thang":
        return f"{d.year}-{d.month:02d}"
    if freq == "Hang quy":
        return f"{d.year}-Q{(d.month - 1) // 3 + 1}"
    if freq == "6 thang":
        return f"{d.year}-H{1 if d.month <= 6 else 2}"
    if freq == "Hang nam":
        return str(d.year)
    return None  # Khi phat sinh -> khong tu sinh


def generate_task_logs():
    """Sinh log cho cac cong viec dinh ky den ky; danh dau tre cac log qua ky."""
    today = nowdate()
    tasks = frappe.get_all("ATTP Task", filters={"active": 1},
                           fields=["name", "title", "task_group", "frequency"])
    for t in tasks:
        key = period_key(t.frequency)
        if not key:
            continue
        if frappe.db.exists("ATTP Task Log", {"task": t.name, "period_key": key}):
            continue
        frappe.get_doc({
            "doctype": "ATTP Task Log", "task": t.name, "title": t.title,
            "task_group": t.task_group, "frequency": t.frequency,
            "period_date": today, "period_key": key, "status": "Cho lam",
        }).insert(ignore_permissions=True)
    mark_overdue()
    frappe.db.commit()


def mark_overdue():
    """Log con 'Cho lam' nhung da sang ky moi -> 'Tre'."""
    for l in frappe.get_all("ATTP Task Log", filters={"status": "Cho lam"},
                            fields=["name", "frequency", "period_key"]):
        cur = period_key(l.frequency)
        if cur and l.period_key and l.period_key != cur:
            frappe.db.set_value("ATTP Task Log", l.name, "status", "Tre")
