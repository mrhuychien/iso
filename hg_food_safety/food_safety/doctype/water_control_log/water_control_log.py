import frappe
from frappe.model.document import Document


class WaterControlLog(Document):
    """Kiem soat nuoc (SSOP1): xac nhan xa dau voi + cam quan moi ca.

    Nguon nuoc do nha may nuoc cap dat QCVN 01-1:2018/BYT; ket qua kiem nghiem
    luu o Lab Test Result (target_type=Nuoc).
    """
    pass
