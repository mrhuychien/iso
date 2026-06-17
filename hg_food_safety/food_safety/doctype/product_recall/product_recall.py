import frappe
from frappe.model.document import Document


class ProductRecall(Document):
    def validate(self):
        if self.qty_shipped:
            self.recovery_pct = round((self.qty_recovered or 0) / self.qty_shipped * 100, 2)
