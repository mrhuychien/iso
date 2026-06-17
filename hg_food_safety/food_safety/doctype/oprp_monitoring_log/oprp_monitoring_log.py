import frappe
from frappe.model.document import Document


class OPRPMonitoringLog(Document):
    """Giam sat OPRP theo ca/lo. Vuot gioi han -> co lap Batch + Non Conformance.

    Logic deviation dat o api/oprp.py (goi qua hooks doc_events) de tach controller
    voi side-effect lien-DocType, de test rieng (handoff nextcode-qa).
    """

    def validate(self):
        # Dong bo co has_deviation ngay tren form (truoc khi submit)
        self.has_deviation = 1 if any(
            (r.status or "").strip().lower() == "khong dat" for r in self.readings
        ) else 0
