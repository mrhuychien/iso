"""Analytics / KPI ATTP - role-gated whitelisted methods (kieu NPP).

Moi method goi _guard() o dong dau. Moi ty le guard chia 0 (tra None).
Khong co Sales Invoice o day - day la KPI chat luong (QC), khong phai doanh so.
"""
import frappe
from frappe import _
from frappe.utils import nowdate, add_days, flt
from hg_food_safety.api._guards import _guard


@frappe.whitelist()
def dashboard_summary() -> dict:
    """Tom tat cho bang dieu khien QA: canh bao + so lieu hom nay."""
    _guard()
    today = nowdate()

    batches_on_hold = frappe.db.count("Batch", {"custom_qc_hold": 1})
    open_nc = frappe.db.count("Non Conformance", {"status": "Open"}) if frappe.db.exists("DocType", "Non Conformance") else 0
    samples_due = frappe.db.count("Sample Retention", {
        "keep_until": ("<=", today), "disposed_on": ("is", "not set")})
    calib_due = frappe.db.count("Calibration Record", {
        "next_due": ("between", [today, add_days(today, 30)])}) if frappe.db.exists("DocType", "Calibration Record") else 0

    return {
        "alerts": {
            "batches_on_hold": batches_on_hold,
            "open_non_conformance": open_nc,
            "samples_due_disposal": samples_due,
            "calibration_due_30d": calib_due,
        },
        "today": {
            "oprp_logs": frappe.db.count("OPRP Monitoring Log", {"log_date": today}),
            "finished_checks": frappe.db.count("Quality Inspection", {"report_date": today}) if frappe.db.has_column("Quality Inspection", "report_date") else 0,
            "foreign_body_checks": frappe.db.count("Foreign Body Check Log", {"log_date": today}),
            "sanitation_logs": frappe.db.count("Sanitation Log", {"log_date": today}),
        },
    }


@frappe.whitelist()
def qc_kpis(from_date: str, to_date: str) -> dict:
    """KPI chat luong trong khoang [from_date, to_date].

    - finished_pass_rate: % Quality Inspection Accepted / tong (Accepted+Rejected).
    - oprp_deviation_rate: % OPRP log co vuot gioi han.
    - mock_recall: thoi gian truy xuat trung binh + % dat muc tieu.
    """
    _guard()

    qi_total = qi_pass = 0
    if frappe.db.exists("DocType", "Quality Inspection"):
        qi_pass = frappe.db.count("Quality Inspection", {"status": "Accepted", "report_date": ("between", [from_date, to_date])}) if frappe.db.has_column("Quality Inspection", "report_date") else frappe.db.count("Quality Inspection", {"status": "Accepted"})
        qi_rej = frappe.db.count("Quality Inspection", {"status": "Rejected", "report_date": ("between", [from_date, to_date])}) if frappe.db.has_column("Quality Inspection", "report_date") else frappe.db.count("Quality Inspection", {"status": "Rejected"})
        qi_total = qi_pass + qi_rej

    oprp_total = frappe.db.count("OPRP Monitoring Log", {"log_date": ("between", [from_date, to_date]), "docstatus": 1})
    oprp_dev = frappe.db.count("OPRP Monitoring Log", {"log_date": ("between", [from_date, to_date]), "docstatus": 1, "has_deviation": 1})

    mock = frappe.get_all("Product Recall", filters={
        "recall_type": "Dien tap", "creation": ("between", [from_date + " 00:00:00", to_date + " 23:59:59"])},
        fields=["trace_time_hours", "meets_target"])
    avg_trace = round(sum(flt(m.trace_time_hours) for m in mock) / len(mock), 2) if mock else None
    met = sum(1 for m in mock if m.meets_target)

    return {
        "period": {"from": from_date, "to": to_date},
        "finished_pass_rate": round(qi_pass / qi_total * 100, 1) if qi_total else None,
        "finished_total": qi_total,
        "oprp_deviation_rate": round(oprp_dev / oprp_total * 100, 1) if oprp_total else None,
        "oprp_total": oprp_total,
        "mock_recall": {"count": len(mock), "avg_trace_hours": avg_trace,
                        "meets_target_pct": round(met / len(mock) * 100, 1) if mock else None},
    }
