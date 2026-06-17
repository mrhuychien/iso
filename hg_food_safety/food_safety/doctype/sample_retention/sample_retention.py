import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class SampleRetention(Document):
    """So luu mau theo lo. Tu tinh keep_until tu Batch (expiry_date) neu chua nhap."""

    def validate(self):
        if self.batch_no and not self.keep_until:
            expiry = frappe.db.get_value("Batch", self.batch_no, "expiry_date")
            if expiry:
                self.keep_until = getdate(expiry)
