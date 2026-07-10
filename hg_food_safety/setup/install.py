"""Setup chay khi cai/migrate app: tao Role, Custom Field, Workflow.

LY DO: patch trong patches.txt bi danh dau hoan thanh (KHONG chay) tren fresh
install. Vi vay setup mac dinh PHAI dat o after_install + after_migrate (idempotent).
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    run_all()


def after_migrate():
    run_all()


def run_all():
    ensure_roles()
    ensure_custom_fields()
    ensure_workflows()
    ensure_tasks()
    ensure_documents()
    frappe.db.commit()


def ensure_roles():
    for role_name in ("FS QC", "FS QA Manager"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)


def ensure_custom_fields():
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


def ensure_workflows():
    from hg_food_safety.patches.v0_1_0.create_workflows import execute as _wf
    _wf()


def ensure_documents():
    from hg_food_safety.setup.catalog import ensure_documents as _seed
    _seed()


SEED_TASKS = [
    # (title, group, frequency, responsible, linked_form, linked_doctype, procedure, role_scope)
    ("Giam sat OPRP theo ca", "Hang ngay / Moi ca", "Moi ca", "KCS", "oprp", "OPRP Monitoring Log", "KH.OPRP.01", "QC"),
    ("Kiem tra di vat / luoi sang / dau do", "Hang ngay / Moi ca", "Moi ca", "KCS", "foreign_body", "Foreign Body Check Log", "QT10", "QC"),
    ("Kiem tra thanh pham moi lo", "Hang ngay / Moi ca", "Hang ngay", "KCS", "", "Quality Inspection", "KH HACCP", "QC"),
    ("Lay mau luu cuoi ngay", "Hang ngay / Moi ca", "Hang ngay", "Ky thuat", "sample", "Sample Retention", "QD.01", "QC"),
    ("Nhat ky ve sinh dau/cuoi ca", "Hang ngay / Moi ca", "Hang ngay", "KCS", "sanitation", "Sanitation Log", "PRP-SSOP2", "QC"),
    ("Xa nuoc dau voi + cam quan nuoc", "Hang ngay / Moi ca", "Hang ngay", "Cong nhan/KCS", "water", "Water Control Log", "PRP-SSOP1", "QC"),
    ("Ghi nhan hang tai che (rework)", "Khi phat sinh", "Khi phat sinh", "KCS", "rework", "Rework Log", "QT10", "QC"),
    ("Diet ruoi muoi khu nha xuong", "Dinh ky ngan", "15 ngay", "Phan xuong", "", "Periodic Sanitation Log", "PRP-SSOP7", "QC"),
    ("Kiem tra thiet bi PCCC", "Dinh ky ngan", "Hang thang", "Van phong", "", "Fire Equipment Log", "QT03", "QA"),
    ("Ve sinh dinh ky + diet con trung/chuot", "Dinh ky ngan", "Hang thang", "Phan xuong", "", "Periodic Sanitation Log", "PRP-SSOP7", "QC"),
    ("Giam sat moi truong (swab be mat/khong khi)", "Dinh ky ngan", "Hang quy", "KCS/Ban ISO", "", "Environmental Monitoring", "KH.KN.01", "QC"),
    ("Bao duong dinh ky thiet bi san xuat", "Dinh ky 6 thang", "6 thang", "Co dien", "", "Asset Maintenance", "QT06", "QA"),
    ("Hieu chuan/kiem dinh thiet bi do", "Dinh ky 6 thang", "6 thang", "Xuong SX", "", "Calibration Record", "QT06", "QA"),
    ("Ra soat danh muc thuy tinh - nhua gion", "Dinh ky 6 thang", "6 thang", "KCS", "", "Glass Brittle Register", "QT10", "QC"),
    ("Kiem nghiem nuoc/san pham dinh ky", "Dinh ky 6 thang", "6 thang", "KCS/Van phong", "lab", "Lab Test Result", "KH.KN.01", "QC"),
    ("Danh gia noi bo toan bo bo phan", "Hang nam", "Hang nam", "Ban ISO", "", "Internal Audit", "QT01", "QA"),
    ("Tham tra he thong HACCP/OPRP", "Hang nam", "Hang nam", "Doi HACCP", "", "Verification Record", "QT04", "QA"),
    ("Xac dinh lai rui ro & co hoi", "Hang nam", "Hang nam", "Ban ISO", "", "Risk Register", "QT05", "QA"),
    ("Tap huan kien thuc VSATTP", "Hang nam", "Hang nam", "Van phong", "", "", "Muc tieu ATTP", "QA"),
    ("Kham suc khoe dinh ky cong nhan", "Hang nam", "Hang nam", "Van phong", "", "", "PRP-SSOP5", "QA"),
    ("Dien tap tinh huong khan cap", "Hang nam", "Hang nam", "Ban ATTP", "", "Emergency Record", "QT03", "QA"),
    ("Dien tap thu hoi (mock recall)", "Hang nam", "Hang nam", "Doi ATTP", "", "Product Recall", "QT02", "QA"),
    ("Danh gia phong ve thuc pham (TACCP/VACCP)", "Hang nam", "Hang nam", "Ban ISO", "", "Food Defense Assessment", "QT11", "QA"),
    ("Tham dinh han su dung (shelf-life)", "Hang nam", "Hang nam", "Ban ISO/Ky thuat", "", "Shelf Life Study", "KH.SL.01", "QA"),
    ("Danh gia & duyet nha cung cap", "Khi phat sinh", "Khi phat sinh", "Mua hang", "", "", "QT07", "QA"),
    ("Kiem tra chat luong hang nhap", "Khi phat sinh", "Khi phat sinh", "KCS/Kho", "", "Quality Inspection", "QT07", "QC"),
    ("Thu hoi san pham mat an toan", "Khi phat sinh", "Khi phat sinh", "Doi ATTP", "", "Product Recall", "QT02", "QA"),
]


def ensure_tasks():
    for (title, group, freq, resp, form, dt, proc, scope) in SEED_TASKS:
        existing = frappe.db.get_value("ATTP Task", {"title": title}, "name")
        if existing:
            # Backfill vai tro phu trach cho ban ghi da co (khi con trong)
            if not frappe.db.get_value("ATTP Task", existing, "role_scope"):
                frappe.db.set_value("ATTP Task", existing, "role_scope", scope)
            continue
        frappe.get_doc({
            "doctype": "ATTP Task", "title": title, "task_group": group,
            "frequency": freq, "responsible": resp, "linked_form": form,
            "linked_doctype": dt or None, "procedure_ref": proc, "active": 1,
            "role_scope": scope,
        }).insert(ignore_permissions=True)
