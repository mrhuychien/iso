import frappe
from frappe.model.document import Document


class SanitationLog(Document):
    """Nhat ky ve sinh hang ngay (gop ve sinh ca nhan + nha xuong).

    KCS xac nhan nhanh moi ca; chi tiet tung hang muc o child Sanitation Item.
    """
    pass
