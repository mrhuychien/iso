import frappe
from frappe.model.document import Document


class ReworkLog(Document):
    def validate(self):
        if not self.like_into_like:
            frappe.throw("Chi duoc tai che 'cung loai vao cung loai' - hay xac nhan o truong tuong ung.")
        if self.rework_qty and self.target_batch:
            bq = frappe.db.get_value('Batch', self.target_batch, 'batch_qty') or 0
            if bq:
                self.rework_pct = round(self.rework_qty / bq * 100, 2)
