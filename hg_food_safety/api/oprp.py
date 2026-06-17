"""Xu ly su kien OPRP Monitoring Log (goi tu hooks doc_events)."""
import frappe
from hg_food_safety.utils import hold_batch, open_non_conformance


def compute_deviation(doc, method=None):
    """validate: bat co has_deviation neu co bat ky reading 'Khong dat'."""
    doc.has_deviation = 1 if any(
        (r.status or "").strip().lower() == "khong dat" for r in doc.readings
    ) else 0


def handle_deviation(doc, method=None):
    """on_submit: neu co vuot gioi han -> co lap lo + mo Non Conformance."""
    if not doc.has_deviation:
        if doc.batch_no:
            frappe.db.set_value("Batch", doc.batch_no, "custom_oprp_ok", 1)
        return
    hold_batch(doc.batch_no, reason=f"OPRP vuot gioi han ({doc.name})")
    open_non_conformance(
        subject=f"OPRP vuot gioi han - lo {doc.batch_no}",
        details=doc.corrective_action or "Vuot gioi han hanh dong OPRP",
        ref_doctype=doc.doctype, ref_name=doc.name,
    )
