import frappe
from frappe.model.document import Document


class ForeignBodyCheckLog(Document):
    """So kiem tra di vat / luoi sang / dau do. Xu ly co lap lo o api/fbc.py (on_submit)."""

    def validate(self):
        # Tu dong dat Khong dat neu dau do bao hoac sang bat thuong
        if self.metal_detector == "Bao" or self.sieve_status == "Bat thuong":
            self.status = "Khong dat"
