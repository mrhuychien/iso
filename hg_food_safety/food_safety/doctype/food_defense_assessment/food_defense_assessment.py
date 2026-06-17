import frappe
from frappe.model.document import Document


class FoodDefenseAssessment(Document):
    def validate(self):
        for r in self.threats:
            r.score = (r.likelihood or 0) * (r.severity or 0)
