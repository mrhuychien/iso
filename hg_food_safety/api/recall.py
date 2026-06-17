"""Ho tro thu hoi: tinh san luong da SX / da xuat tu Stock Ledger theo lo."""
import frappe
from frappe import _
from hg_food_safety.api._guards import _guard


@frappe.whitelist()
def prefill_from_batch(batch_no: str) -> dict:
    """Goi y so da SX / da xuat / ton kho cho mot lo (tu Stock Ledger Entry).

    Manager-only. Tra so luong de QA dien nhanh vao Product Recall.
    """
    _guard()
    if not frappe.db.exists("Batch", batch_no):
        frappe.throw(_("Lo khong ton tai"))
    # Stock Ledger Entry: actual_qty > 0 la nhap (san xuat), < 0 la xuat.
    rows = frappe.get_all("Stock Ledger Entry",
        filters={"batch_no": batch_no, "is_cancelled": 0},
        fields=["actual_qty"])
    produced = sum(r.actual_qty for r in rows if r.actual_qty > 0)
    shipped = sum(-r.actual_qty for r in rows if r.actual_qty < 0)
    item = frappe.db.get_value("Batch", batch_no, "item")
    return {
        "batch_no": batch_no, "item": item,
        "qty_produced": produced, "qty_shipped": shipped,
        "qty_stock": produced - shipped,
    }
