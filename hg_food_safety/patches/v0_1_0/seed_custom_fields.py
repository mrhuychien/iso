import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Them custom field ATTP vao Batch / Item / Supplier. Idempotent (insert_after-safe)."""
    fields = {
        "Batch": [
            {"fieldname": "custom_qc_status", "label": "Trang thai ATTP", "fieldtype": "Select",
             "options": "\nDang san xuat\nDat\nCo lap\nHuy", "insert_after": "batch_qty"},
            {"fieldname": "custom_qc_hold", "label": "Co lap (QC Hold)", "fieldtype": "Check",
             "insert_after": "custom_qc_status"},
            {"fieldname": "custom_oprp_ok", "label": "OPRP trong tam kiem soat", "fieldtype": "Check",
             "insert_after": "custom_qc_hold"},
        ],
        "Item": [
            {"fieldname": "custom_fs_category", "label": "Nhom ATTP", "fieldtype": "Select",
             "options": "\nThanh pham\nNguyen vat lieu\nPhu gia - Pham mau\nBao bi", "insert_after": "item_group"},
            {"fieldname": "custom_storage_condition", "label": "Dieu kien bao quan", "fieldtype": "Small Text",
             "insert_after": "custom_fs_category"},
            {"fieldname": "custom_qc_required_docs", "label": "Ho so yeu cau khi nhap", "fieldtype": "Small Text",
             "insert_after": "custom_storage_condition"},
            {"fieldname": "custom_legal_basis", "label": "Can cu TCVN/QCVN", "fieldtype": "Small Text",
             "insert_after": "custom_qc_required_docs"},
        ],
        "Supplier": [
            {"fieldname": "custom_approved", "label": "NCC duoc duyet", "fieldtype": "Check",
             "insert_after": "supplier_group"},
            {"fieldname": "custom_reeval_date", "label": "Ngay tai danh gia", "fieldtype": "Date",
             "insert_after": "custom_approved"},
        ],
    }
    create_custom_fields(fields, ignore_validate=True)
