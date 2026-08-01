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
    retire_tasks()
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
    ("Kiem tra thanh pham moi lo", "Hang ngay / Moi ca", "Hang ngay", "KCS", "", "Quality Inspection", "KH HACCP", "QC"),
    ("Lay mau luu cuoi ngay", "Hang ngay / Moi ca", "Hang ngay", "Ky thuat", "sample", "Sample Retention", "QD.01", "QC"),
    ("Nhat ky ve sinh dau/cuoi ca", "Hang ngay / Moi ca", "Hang ngay", "KCS", "sanitation", "Sanitation Log", "PRP-SSOP2", "QC"),
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

    # ── Bo sung theo "Lich cong viec ATTP Hoang Giang.xlsx" (ban goc, 40 viec) ──
    # Hang ngay / Moi ca (KCS tac nghiep tai xuong)
    ("Kiem tra ve sinh ca nhan - suc khoe - bao ho cong nhan", "Hang ngay / Moi ca", "Hang ngay", "KCS / To truong", "", "", "PRP-SSOP4,5", "QC"),
    ("Kiem soat lay nhiem cheo trong san xuat", "Hang ngay / Moi ca", "Hang ngay", "KCS / Truong ca", "", "", "PRP-SSOP3", "QC"),
    ("Thu gom - xu ly chat thai trong va sau san xuat", "Hang ngay / Moi ca", "Hang ngay", "Phan xuong / KCS", "", "", "PRP-SSOP6", "QC"),
    ("Kiem tra khoi luong - hinh dang vien banh (>=3 lan/ca/may)", "Hang ngay / Moi ca", "Moi ca", "Cong nhan SX", "", "", "QT08", "QC"),
    ("Kiem tra do kin moi han nilon khi dong goi (>=2 lan/ca)", "Hang ngay / Moi ca", "Moi ca", "Quan ly SX", "", "", "QT08", "QC"),
    ("Kiem tra tinh trang thiet bi san xuat", "Hang ngay / Moi ca", "Hang ngay", "Co dien / Phan xuong", "", "", "QT06", "QC"),
    # Dinh ky ngan
    ("Lay ket qua kiem nghiem chat luong nuoc tu nha cung cap", "Dinh ky ngan", "Hang thang", "KCS / Van phong", "", "", "PRP-SSOP1", "QC"),
    ("Theo doi tinh hinh phat sinh dich benh", "Dinh ky ngan", "Hang thang", "Van phong", "", "", "QT03", "QA"),
    ("Diet chuot toan bo khu vuc nha xuong", "Dinh ky ngan", "Hang quy", "Phan xuong", "", "", "PRP-SSOP7", "QC"),
    # Dinh ky 6 thang
    ("Ve sinh tran nha - quat thong gio - bong den - tu dien", "Dinh ky 6 thang", "6 thang", "Phan xuong", "", "", "PRP-SSOP", "QC"),
    # Hang nam
    ("Cap nhat boi canh to chuc", "Hang nam", "Hang nam", "Ban ISO", "", "", "QT05", "QA"),
    ("Hop xem xet cua lanh dao", "Hang nam", "Hang nam", "Ban lanh dao", "", "", "QT01", "QA"),
    ("Cap nhat muc tieu ATTP nam va ke hoach thuc hien", "Hang nam", "Hang nam", "Ban lanh dao", "", "", "Chinh sach - Muc tieu", "QA"),
    ("Thau rua - ve sinh be nuoc", "Hang nam", "Hang nam", "Phan xuong", "", "", "KH HACCP", "QC"),
    ("Ra soat ho so het han luu - lap bien ban huy", "Hang nam", "Hang nam", "Truong bo phan", "", "", "QT01", "QA"),
    ("Cap nhat danh muc tai lieu noi bo/ben ngoai/ho so", "Hang nam", "Hang nam", "Ban ISO / Cac bo phan", "", "", "QT01", "QA"),
    # Khi phat sinh
    ("Sua doi - ban hanh tai lieu", "Khi phat sinh", "Khi phat sinh", "Bo phan de nghi / Ban ISO", "", "Doc Change Request", "QT01", "QA"),
    ("Kiem soat su khong phu hop & hanh dong khac phuc", "Khi phat sinh", "Khi phat sinh", "Truong bo phan / Ban ISO", "", "Non Conformance", "QT01", "QA"),
    ("Sua chua thiet bi khi co su co", "Khi phat sinh", "Khi phat sinh", "Co dien / Giam doc", "", "", "QT06", "QC"),
    ("Ung pho tinh huong khan cap (hoa hoan - bao lu - dich benh)", "Khi phat sinh", "Khi phat sinh", "Ban ATTP / Van phong", "", "", "QT03", "QA"),
    ("Xu ly san pham khach hang tra ve", "Khi phat sinh", "Khi phat sinh", "Bo phan dong goi / KCS", "", "", "QT02", "QC"),
]


# Danh muc kiem soat (nghiep vu) cho tung cong viec -> nhom tren portal.
D_NL = "Kiem soat nguyen lieu - NCC"
D_HT = "Kiem soat hien truong - ve sinh"
D_SX = "Kiem soat qua trinh san xuat"
D_TP = "Kiem soat thanh pham - luu mau"
D_NM = "Kiem soat nuoc - moi truong"
D_TB = "Thiet bi - hieu chuan"
D_AT = "An toan - ung pho su co"
D_TH = "Thu hoi - truy xuat"
D_CN = "Con nguoi - dao tao"
D_HS = "He thong - tai lieu"

TASK_DOMAIN = {
    # Nguyen lieu & nha cung cap
    "Danh gia & duyet nha cung cap": D_NL,
    "Kiem tra chat luong hang nhap": D_NL,
    # Hien truong & ve sinh
    "Nhat ky ve sinh dau/cuoi ca": D_HT,
    "Kiem tra ve sinh ca nhan - suc khoe - bao ho cong nhan": D_HT,
    "Kiem soat lay nhiem cheo trong san xuat": D_HT,
    "Thu gom - xu ly chat thai trong va sau san xuat": D_HT,
    "Diet ruoi muoi khu nha xuong": D_HT,
    "Ve sinh dinh ky + diet con trung/chuot": D_HT,
    "Diet chuot toan bo khu vuc nha xuong": D_HT,
    "Ve sinh tran nha - quat thong gio - bong den - tu dien": D_HT,
    # Qua trinh san xuat
    "Kiem tra khoi luong - hinh dang vien banh (>=3 lan/ca/may)": D_SX,
    "Kiem tra do kin moi han nilon khi dong goi (>=2 lan/ca)": D_SX,
    "Ghi nhan hang tai che (rework)": D_SX,
    "Ra soat danh muc thuy tinh - nhua gion": D_SX,
    # Thanh pham & luu mau
    "Kiem tra thanh pham moi lo": D_TP,
    "Lay mau luu cuoi ngay": D_TP,
    "Tham dinh han su dung (shelf-life)": D_TP,
    # Nuoc & moi truong
    "Lay ket qua kiem nghiem chat luong nuoc tu nha cung cap": D_NM,
    "Giam sat moi truong (swab be mat/khong khi)": D_NM,
    "Kiem nghiem nuoc/san pham dinh ky": D_NM,
    "Thau rua - ve sinh be nuoc": D_NM,
    # Thiet bi & hieu chuan
    "Kiem tra tinh trang thiet bi san xuat": D_TB,
    "Bao duong dinh ky thiet bi san xuat": D_TB,
    "Hieu chuan/kiem dinh thiet bi do": D_TB,
    "Sua chua thiet bi khi co su co": D_TB,
    # An toan & ung pho su co
    "Kiem tra thiet bi PCCC": D_AT,
    "Theo doi tinh hinh phat sinh dich benh": D_AT,
    "Dien tap tinh huong khan cap": D_AT,
    "Ung pho tinh huong khan cap (hoa hoan - bao lu - dich benh)": D_AT,
    "Danh gia phong ve thuc pham (TACCP/VACCP)": D_AT,
    # Thu hoi & truy xuat
    "Dien tap thu hoi (mock recall)": D_TH,
    "Thu hoi san pham mat an toan": D_TH,
    "Xu ly san pham khach hang tra ve": D_TH,
    # Con nguoi & dao tao
    "Tap huan kien thuc VSATTP": D_CN,
    "Kham suc khoe dinh ky cong nhan": D_CN,
    # He thong & tai lieu
    "Danh gia noi bo toan bo bo phan": D_HS,
    "Tham tra he thong HACCP/OPRP": D_HS,
    "Xac dinh lai rui ro & co hoi": D_HS,
    "Cap nhat boi canh to chuc": D_HS,
    "Hop xem xet cua lanh dao": D_HS,
    "Cap nhat muc tieu ATTP nam va ke hoach thuc hien": D_HS,
    "Ra soat ho so het han luu - lap bien ban huy": D_HS,
    "Cap nhat danh muc tai lieu noi bo/ben ngoai/ho so": D_HS,
    "Sua doi - ban hanh tai lieu": D_HS,
    "Kiem soat su khong phu hop & hanh dong khac phuc": D_HS,
}


# Cong viec da bo khoi checklist. Giu ban ghi ATTP Task + cac log "Da lam"
# de con ho so truy vet, chi ngung sinh ky moi va don cac ky chua lam.
RETIRED_TASKS = [
    "Giam sat OPRP theo ca",
    "Kiem tra di vat / luoi sang / dau do",
    "Xa nuoc dau voi + cam quan nuoc",
]


def retire_tasks():
    """Tat cong viec da bo (idempotent, chay moi lan migrate)."""
    for title in RETIRED_TASKS:
        name = frappe.db.get_value("ATTP Task", {"title": title}, "name")
        if not name:
            continue
        if frappe.db.get_value("ATTP Task", name, "active"):
            frappe.db.set_value("ATTP Task", name, "active", 0)
        # Ky chua lam khong con ap dung -> xoa; log "Da lam" van giu nguyen.
        for log in frappe.get_all("ATTP Task Log",
                                  filters={"task": name, "status": ["in", ["Cho lam", "Tre"]]},
                                  pluck="name"):
            frappe.delete_doc("ATTP Task Log", log, force=1, ignore_permissions=True)


def ensure_tasks():
    for (title, group, freq, resp, form, dt, proc, scope) in SEED_TASKS:
        domain = TASK_DOMAIN.get(title)
        existing = frappe.db.get_value("ATTP Task", {"title": title}, "name")
        if existing:
            # Backfill vai tro / danh muc cho ban ghi da co (khi con trong)
            if not frappe.db.get_value("ATTP Task", existing, "role_scope"):
                frappe.db.set_value("ATTP Task", existing, "role_scope", scope)
            if domain and not frappe.db.get_value("ATTP Task", existing, "task_domain"):
                frappe.db.set_value("ATTP Task", existing, "task_domain", domain)
            continue
        frappe.get_doc({
            "doctype": "ATTP Task", "title": title, "task_group": group,
            "frequency": freq, "responsible": resp, "linked_form": form,
            "linked_doctype": dt or None, "procedure_ref": proc, "active": 1,
            "role_scope": scope, "task_domain": domain,
        }).insert(ignore_permissions=True)
