"""Xu ly su kien Foreign Body Check Log."""
import frappe
from hg_food_safety.utils import hold_batch, open_non_conformance


def handle_fail(doc, method=None):
    """on_submit: di vat/dau do bao/sang bat thuong -> co lap lo + Non Conformance."""
    if doc.status != "Khong dat":
        return
    reason = "Phat hien di vat / dau do bao / luoi sang bat thuong"
    hold_batch(doc.batch_no, reason=f"{reason} ({doc.name})")
    open_non_conformance(
        subject=f"Di vat - lo {doc.batch_no or doc.name}",
        details=doc.action or reason,
        ref_doctype=doc.doctype, ref_name=doc.name,
    )
