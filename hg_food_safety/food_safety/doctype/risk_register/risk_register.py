import frappe
from frappe.model.document import Document


class RiskRegister(Document):
    def validate(self):
        self.level = (self.likelihood or 0) * (self.consequence or 0)
