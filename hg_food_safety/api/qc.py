"""Xu ly Quality Inspection (core) cho thanh pham/NVL: reject -> co lap lo."""
import frappe
from hg_food_safety.utils import hold_batch, open_non_conformance


def on_inspection_submit(doc, method=None):
    """on_submit Quality Inspection: neu status=Rejected -> co lap Batch lien quan."""
    if doc.status != "Rejected":
        return
    batch_no = getattr(doc, "batch_no", None)
    if batch_no:
        hold_batch(batch_no, reason=f"Quality Inspection {doc.name} - Rejected")
    open_non_conformance(
        subject=f"Quality Inspection Rejected - {doc.item_code or ''} (lo {batch_no or '-'})",
        details=f"Quality Inspection {doc.name} bi tu choi.",
        ref_doctype=doc.doctype, ref_name=doc.name,
    )
