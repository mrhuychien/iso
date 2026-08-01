"""API cho portal SPA: cong viec theo lich, tao ban ghi, tai lieu noi bo. Guard require_fs."""
import json
import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime
from hg_food_safety.api._guards import require_fs, is_manager, _guard

ALLOWED_CREATE = {
    "OPRP Monitoring Log", "Foreign Body Check Log", "Sanitation Log",
    "Water Control Log", "Sample Retention", "Rework Log", "Lab Test Result",
}
ALLOWED_LINK = {"Batch", "Item", "Employee"}
GROUP_ORDER = ["Hang ngay / Moi ca", "Dinh ky ngan", "Dinh ky 6 thang", "Hang nam", "Khi phat sinh"]

# Danh muc kiem soat (nghiep vu) — thu tu hien thi tren portal
DOMAIN_ORDER = [
    "Kiem soat nguyen lieu - NCC", "Kiem soat hien truong - ve sinh",
    "Kiem soat qua trinh san xuat", "Kiem soat thanh pham - luu mau",
    "Kiem soat nuoc - moi truong", "Thiet bi - hieu chuan",
    "An toan - ung pho su co", "Thu hoi - truy xuat",
    "Con nguoi - dao tao", "He thong - tai lieu",
]
DOMAIN_VI = {
    "Kiem soat nguyen lieu - NCC": "Kiểm soát nguyên liệu & nhà cung cấp",
    "Kiem soat hien truong - ve sinh": "Kiểm soát hiện trường & vệ sinh",
    "Kiem soat qua trinh san xuat": "Kiểm soát quá trình sản xuất",
    "Kiem soat thanh pham - luu mau": "Kiểm soát thành phẩm & lưu mẫu",
    "Kiem soat nuoc - moi truong": "Kiểm soát nước & môi trường",
    "Thiet bi - hieu chuan": "Thiết bị & hiệu chuẩn",
    "An toan - ung pho su co": "An toàn & ứng phó sự cố",
    "Thu hoi - truy xuat": "Thu hồi & truy xuất",
    "Con nguoi - dao tao": "Con người & đào tạo",
    "He thong - tai lieu": "Hệ thống & tài liệu",
}
DOMAIN_ICON = {
    "Kiem soat nguyen lieu - NCC": "inventory_2",
    "Kiem soat hien truong - ve sinh": "cleaning_services",
    "Kiem soat qua trinh san xuat": "precision_manufacturing",
    "Kiem soat thanh pham - luu mau": "inventory",
    "Kiem soat nuoc - moi truong": "water_drop",
    "Thiet bi - hieu chuan": "build",
    "An toan - ung pho su co": "local_fire_department",
    "Thu hoi - truy xuat": "sync_problem",
    "Con nguoi - dao tao": "groups",
    "He thong - tai lieu": "folder_managed",
}

# Nhan hien thi co dau (DB luu ASCII de khop logic period_key / GROUP_ORDER).
GROUP_VI = {
    "Hang ngay / Moi ca": "Hằng ngày / Mỗi ca",
    "Dinh ky ngan": "Định kỳ ngắn",
    "Dinh ky 6 thang": "Định kỳ 6 tháng",
    "Hang nam": "Hằng năm",
    "Khi phat sinh": "Khi phát sinh",
}
FREQ_VI = {
    "Hang ngay": "Hằng ngày", "Moi ca": "Mỗi ca", "15 ngay": "15 ngày",
    "Hang thang": "Hằng tháng", "Hang quy": "Hằng quý", "6 thang": "6 tháng",
    "Hang nam": "Hằng năm", "Khi phat sinh": "Khi phát sinh",
}
# Thu tu hien thi khi gom theo TAN SUAT: chu ky ngan (gap nhat) len truoc.
FREQ_ORDER = ["Moi ca", "Hang ngay", "15 ngay", "Hang thang",
              "Hang quy", "6 thang", "Hang nam", "Khi phat sinh"]
FREQ_ICON = {
    "Moi ca": "schedule", "Hang ngay": "today", "15 ngay": "date_range",
    "Hang thang": "calendar_month", "Hang quy": "event_repeat",
    "6 thang": "calendar_view_month", "Hang nam": "event",
    "Khi phat sinh": "bolt",
}
TASK_VI = {
    "Giam sat OPRP theo ca": "Giám sát OPRP theo ca",
    "Kiem tra di vat / luoi sang / dau do": "Kiểm tra dị vật / lưới sàng / đầu dò",
    "Kiem tra thanh pham moi lo": "Kiểm tra thành phẩm mỗi lô",
    "Lay mau luu cuoi ngay": "Lấy mẫu lưu cuối ngày",
    "Nhat ky ve sinh dau/cuoi ca": "Nhật ký vệ sinh đầu/cuối ca",
    "Xa nuoc dau voi + cam quan nuoc": "Xả nước đầu vòi + cảm quan nước",
    "Ghi nhan hang tai che (rework)": "Ghi nhận hàng tái chế (rework)",
    "Diet ruoi muoi khu nha xuong": "Diệt ruồi muỗi khu nhà xưởng",
    "Kiem tra thiet bi PCCC": "Kiểm tra thiết bị PCCC",
    "Ve sinh dinh ky + diet con trung/chuot": "Vệ sinh định kỳ + diệt côn trùng/chuột",
    "Giam sat moi truong (swab be mat/khong khi)": "Giám sát môi trường (swab bề mặt/không khí)",
    "Bao duong dinh ky thiet bi san xuat": "Bảo dưỡng định kỳ thiết bị sản xuất",
    "Hieu chuan/kiem dinh thiet bi do": "Hiệu chuẩn/kiểm định thiết bị đo",
    "Ra soat danh muc thuy tinh - nhua gion": "Rà soát danh mục thủy tinh - nhựa giòn",
    "Kiem nghiem nuoc/san pham dinh ky": "Kiểm nghiệm nước/sản phẩm định kỳ",
    "Danh gia noi bo toan bo bo phan": "Đánh giá nội bộ toàn bộ bộ phận",
    "Tham tra he thong HACCP/OPRP": "Thẩm tra hệ thống HACCP/OPRP",
    "Xac dinh lai rui ro & co hoi": "Xác định lại rủi ro & cơ hội",
    "Tap huan kien thuc VSATTP": "Tập huấn kiến thức VSATTP",
    "Kham suc khoe dinh ky cong nhan": "Khám sức khỏe định kỳ công nhân",
    "Dien tap tinh huong khan cap": "Diễn tập tình huống khẩn cấp",
    "Dien tap thu hoi (mock recall)": "Diễn tập thu hồi (mock recall)",
    "Danh gia phong ve thuc pham (TACCP/VACCP)": "Đánh giá phòng vệ thực phẩm (TACCP/VACCP)",
    "Tham dinh han su dung (shelf-life)": "Thẩm định hạn sử dụng (shelf-life)",
    "Danh gia & duyet nha cung cap": "Đánh giá & duyệt nhà cung cấp",
    "Kiem tra chat luong hang nhap": "Kiểm tra chất lượng hàng nhập",
    "Thu hoi san pham mat an toan": "Thu hồi sản phẩm mất an toàn",
    # Bo sung theo lich cong viec goc
    "Kiem tra ve sinh ca nhan - suc khoe - bao ho cong nhan": "Kiểm tra vệ sinh cá nhân, sức khỏe, bảo hộ công nhân",
    "Kiem soat lay nhiem cheo trong san xuat": "Kiểm soát lây nhiễm chéo trong sản xuất",
    "Thu gom - xu ly chat thai trong va sau san xuat": "Thu gom, xử lý chất thải trong và sau sản xuất",
    "Kiem tra khoi luong - hinh dang vien banh (>=3 lan/ca/may)": "Kiểm tra khối lượng, hình dạng viên bánh (≥3 lần/ca/máy)",
    "Kiem tra do kin moi han nilon khi dong goi (>=2 lan/ca)": "Kiểm tra độ kín mối hàn nilon khi đóng gói (≥2 lần/ca)",
    "Kiem tra tinh trang thiet bi san xuat": "Kiểm tra tình trạng thiết bị sản xuất",
    "Lay ket qua kiem nghiem chat luong nuoc tu nha cung cap": "Lấy kết quả kiểm nghiệm chất lượng nước từ nhà cung cấp",
    "Theo doi tinh hinh phat sinh dich benh": "Theo dõi tình hình phát sinh dịch bệnh",
    "Diet chuot toan bo khu vuc nha xuong": "Diệt chuột toàn bộ khu vực nhà xưởng",
    "Ve sinh tran nha - quat thong gio - bong den - tu dien": "Vệ sinh trần nhà, quạt thông gió, bóng đèn, tủ điện",
    "Cap nhat boi canh to chuc": "Cập nhật bối cảnh tổ chức",
    "Hop xem xet cua lanh dao": "Họp xem xét của lãnh đạo",
    "Cap nhat muc tieu ATTP nam va ke hoach thuc hien": "Cập nhật mục tiêu ATTP năm và kế hoạch thực hiện",
    "Thau rua - ve sinh be nuoc": "Thau rửa, vệ sinh bể nước",
    "Ra soat ho so het han luu - lap bien ban huy": "Rà soát hồ sơ hết hạn lưu, lập biên bản hủy",
    "Cap nhat danh muc tai lieu noi bo/ben ngoai/ho so": "Cập nhật danh mục tài liệu nội bộ/bên ngoài/hồ sơ",
    "Sua doi - ban hanh tai lieu": "Sửa đổi, ban hành tài liệu",
    "Kiem soat su khong phu hop & hanh dong khac phuc": "Kiểm soát sự không phù hợp & hành động khắc phục",
    "Sua chua thiet bi khi co su co": "Sửa chữa thiết bị khi có sự cố",
    "Ung pho tinh huong khan cap (hoa hoan - bao lu - dich benh)": "Ứng phó tình huống khẩn cấp (hỏa hoạn, bão lũ, dịch bệnh)",
    "Xu ly san pham khach hang tra ve": "Xử lý sản phẩm khách hàng trả về",
}


def _ensure_today():
    """Tu seed ATTP Task (neu trong) + sinh log den ky -> list luon co viec hien."""
    try:
        if not frappe.db.count("ATTP Task"):
            from hg_food_safety.setup.install import ensure_tasks
            ensure_tasks()
        from hg_food_safety.schedule import generate_task_logs
        generate_task_logs()
    except Exception:
        frappe.log_error(title="today_tasks ensure")


def _fs_role():
    """Vai tro dang dung app: QA (quan ly) hoac QC (KCS)."""
    return "QA" if is_manager() else "QC"


def _task_visible(scope, role):
    return (scope or "Chung") in ("Chung", role)


@frappe.whitelist()
def today_tasks() -> dict:
    """Cong viec dang cho/tre theo VAI TRO dang dung (QC vs QA), gom theo nhom."""
    require_fs()
    _ensure_today()
    role = _fs_role()
    logs = frappe.get_all("ATTP Task Log",
        filters={"status": ["in", ["Cho lam", "Tre"]]},
        fields=["name", "task", "title", "task_group", "frequency", "status", "period_date"],
        order_by="period_date asc")
    cache = {}
    def task_info(task):
        if task not in cache:
            cache[task] = frappe.db.get_value(
                "ATTP Task", task, ["linked_form", "role_scope", "task_domain"], as_dict=True) or {}
        return cache[task]
    # Moi CONG VIEC chi hien 1 dong: giu ky moi nhat, dem so ky cu con ton.
    per_task = {}
    for l in logs:
        info = task_info(l.task)
        if not _task_visible(info.get("role_scope"), role):
            continue
        cur = per_task.get(l.task)
        if cur is None:
            l["missed"] = 0
            l["_domain"] = info.get("task_domain") or "Khac"
            l["linked_form"] = info.get("linked_form") or ""
            per_task[l.task] = l
        elif (l.period_date or "") > (cur.period_date or ""):
            l["missed"] = cur["missed"] + 1
            l["_domain"] = cur["_domain"]
            l["linked_form"] = cur["linked_form"]
            if cur.status == "Tre":
                l["status"] = "Tre"
            per_task[l.task] = l
        else:
            cur["missed"] += 1
            if l.status == "Tre":
                cur["status"] = "Tre"

    by_domain, by_freq = {}, {}
    visible = []
    for l in per_task.values():
        freq_raw = l.frequency
        l["title"] = TASK_VI.get(l.title, l.title)
        l["frequency"] = FREQ_VI.get(freq_raw, freq_raw)
        l["task_group"] = GROUP_VI.get(l.task_group, l.task_group)
        by_domain.setdefault(l.pop("_domain"), []).append(l)
        by_freq.setdefault(freq_raw or "Khac", []).append(l)
        visible.append(l)

    def _order(buckets, keys, label, icons, fallback_label):
        out = [{"group": label.get(k, k), "icon": icons.get(k, "task_alt"), "tasks": buckets[k]}
               for k in keys if k in buckets]
        out += [{"group": label.get(k, fallback_label), "icon": "task_alt", "tasks": buckets[k]}
                for k in buckets if k not in keys]
        return out

    ordered = _order(by_domain, DOMAIN_ORDER, DOMAIN_VI, DOMAIN_ICON, "Khác")
    ordered_freq = _order(by_freq, FREQ_ORDER, FREQ_VI, FREQ_ICON, "Khác")
    done_logs = frappe.get_all("ATTP Task Log",
        filters={"status": "Da lam", "done_on": [">=", nowdate() + " 00:00:00"]}, fields=["task"])
    done_today = sum(1 for d in done_logs if _task_visible(task_info(d.task).get("role_scope"), role))
    return {
        "date": nowdate(),
        "role": role,
        "is_manager": is_manager(),
        "groups": ordered,
        "groups_freq": ordered_freq,
        "open_count": len(visible),
        "overdue_count": sum(1 for l in visible if l.status == "Tre"),
        "done_today": done_today,
        "batches_on_hold": frappe.db.count("Batch", {"custom_qc_hold": 1}) if frappe.db.has_column("Batch", "custom_qc_hold") else 0,
    }


def _close_older_open(task, keep_log, period_date):
    """Dong cac ky cu con mo cua cung cong viec -> moi viec chi con 1 dong."""
    for old in frappe.get_all("ATTP Task Log",
                              filters={"task": task, "status": ["in", ["Cho lam", "Tre"]],
                                       "name": ["!=", keep_log]},
                              fields=["name", "period_date"]):
        if not period_date or (old.period_date and old.period_date <= period_date):
            frappe.db.set_value("ATTP Task Log", old.name, "status", "Bo lo")


@frappe.whitelist()
def mark_task_done(log: str, note: str = None) -> dict:
    """Danh dau mot cong viec da lam (cho cong viec khong gan bieu mau)."""
    require_fs()
    doc = frappe.get_doc("ATTP Task Log", log)
    doc.status = "Da lam"
    doc.done_by = frappe.session.user
    doc.done_on = now_datetime()
    if note:
        doc.note = note
    doc.save(ignore_permissions=True)
    _close_older_open(doc.task, doc.name, doc.period_date)
    return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def search_link(doctype: str, txt: str = "") -> list:
    """Tim ban ghi cho truong Link tren portal."""
    require_fs()
    if doctype not in ALLOWED_LINK:
        frappe.throw(_("Khong duoc phep tra cuu DocType nay"), frappe.PermissionError)
    txt = (txt or "").strip()
    fields = ["name"] + (["employee_name"] if doctype == "Employee" else (["item_name"] if doctype == "Item" else []))
    rows = frappe.get_all(doctype, or_filters={"name": ["like", f"%{txt}%"]} if txt else None,
                          fields=fields, limit_page_length=12, order_by="modified desc")
    out = []
    for r in rows:
        label = r.get("employee_name") or r.get("item_name") or r["name"]
        out.append({"value": r["name"], "label": f"{r['name']} - {label}" if label != r["name"] else r["name"]})
    return out


@frappe.whitelist()
def create_record(doctype: str, payload, submit: int = 0) -> dict:
    """Tao ban ghi tac nghiep tu portal (permission do Frappe kiem). Tu danh dau cong viec lien quan."""
    require_fs()
    if doctype not in ALLOWED_CREATE:
        frappe.throw(_("Khong duoc phep tao DocType nay tu portal"), frappe.PermissionError)
    data = json.loads(payload) if isinstance(payload, str) else (payload or {})
    meta = frappe.get_meta(doctype)
    valid = {df.fieldname for df in meta.fields}
    doc = frappe.new_doc(doctype)
    for k, v in data.items():
        if k in valid:
            doc.set(k, v)
    doc.insert()
    if int(submit or 0) and meta.is_submittable:
        doc.submit()
    _auto_complete_task(doctype, doc.name)
    return {"name": doc.name, "docstatus": doc.docstatus}


def _auto_complete_task(doctype, docname):
    """Danh dau log cong viec dang mo co linked_doctype trung -> Da lam."""
    try:
        logs = frappe.get_all("ATTP Task Log",
            filters={"status": ["in", ["Cho lam", "Tre"]], "reference_name": ["is", "not set"]},
            fields=["name", "task"], order_by="period_date desc")
        for lg in logs:
            if frappe.db.get_value("ATTP Task", lg.task, "linked_doctype") == doctype:
                frappe.db.set_value("ATTP Task Log", lg.name, {
                    "status": "Da lam", "done_by": frappe.session.user,
                    "done_on": now_datetime(), "reference_doctype": doctype, "reference_name": docname})
                _close_older_open(lg.task, lg.name,
                                  frappe.db.get_value("ATTP Task Log", lg.name, "period_date"))
                break
    except Exception:
        frappe.log_error(title="auto_complete_task")


# ─────────────── Tai lieu noi bo ───────────────
DOC_TYPES = ("Noi bo", "Ben ngoai")
DOC_STATUS = ("Hieu luc", "Da thay the", "Het hieu luc")
DOC_CATS = ("Chinh sach - Muc tieu", "So tay - PRP/SSOP", "Ke hoach (HACCP/OPRP/KN/SL)",
            "Quy trinh (QT)", "Quy dinh (QD)", "Bieu mau - Ho so (BM)",
            "Danh muc - Dinh muc", "Tai lieu ben ngoai")
# Nhom tai lieu KCS (QC) duoc thay tren portal (tac nghiep). QA thay tat ca.
QC_DOC_CATS = {"Quy trinh (QT)", "Ke hoach (HACCP/OPRP/KN/SL)", "Quy dinh (QD)",
               "Bieu mau - Ho so (BM)", "Danh muc - Dinh muc"}


@frappe.whitelist()
def documents() -> list:
    """Danh muc tai lieu kiem soat (noi bo + ben ngoai), kem so lan cap nhat. Vai tro FS deu xem duoc."""
    require_fs()
    rows = frappe.get_all("Controlled Document",
        fields=["name", "doc_name", "doc_code", "doc_category", "doc_type", "version", "status",
                "approval_status", "attachment", "signed_pdf", "summary", "location", "retention",
                "effective_date", "modified"],
        order_by="doc_code asc, modified desc")
    if not is_manager():
        # KCS (QC): chi thay ho so/bieu mau + quy trinh/ke hoach can dung khi tac nghiep
        rows = [r for r in rows if r.get("doc_category") in QC_DOC_CATS]
    for r in rows:
        r["change_count"] = frappe.db.count("Controlled Document Change", {"parent": r["name"]})
    return rows


@frappe.whitelist()
def document_get(name: str) -> dict:
    """Chi tiet day du mot tai lieu (gom noi dung). Vai tro FS deu xem duoc."""
    require_fs()
    d = frappe.get_doc("Controlled Document", name)
    return {
        "name": d.name, "doc_name": d.doc_name, "doc_code": d.doc_code,
        "doc_category": d.doc_category, "doc_type": d.doc_type, "version": d.version,
        "status": d.status, "approval_status": d.approval_status or "Da duyet",
        "location": d.location, "retention": d.retention, "effective_date": str(d.effective_date or ""),
        "summary": d.summary, "content": d.content, "attachment": d.attachment,
        "signed_pdf": d.signed_pdf, "approved_by": d.approved_by,
        "approved_on": str(d.approved_on or ""), "modified": str(d.modified or ""),
        "change_count": frappe.db.count("Controlled Document Change", {"parent": d.name}),
    }


@frappe.whitelist()
def document_history(name: str) -> list:
    """Lich su cap nhat cua mot tai lieu (moi -> cu)."""
    require_fs()
    return frappe.get_all("Controlled Document Change",
        filters={"parent": name, "parenttype": "Controlled Document"},
        fields=["changed_on", "changed_by", "action", "version", "note"],
        order_by="changed_on desc, idx desc")


def _add_change(doc, action, note=None):
    doc.append("change_log", {
        "changed_on": now_datetime(), "changed_by": frappe.session.user,
        "action": action, "version": doc.version or "", "note": note or "",
    })


@frappe.whitelist()
def create_document(doc_name: str, doc_code: str = None, doc_category: str = None,
                    doc_type: str = "Noi bo", version: str = None, status: str = "Hieu luc",
                    attachment: str = None, summary: str = None, location: str = None,
                    retention: str = None) -> dict:
    """Them tai lieu vao danh muc (chi quan ly QA). attachment = file_url da upload."""
    _guard()
    doc = frappe.get_doc({
        "doctype": "Controlled Document", "doc_name": doc_name, "doc_code": doc_code,
        "doc_category": doc_category if doc_category in DOC_CATS else None,
        "doc_type": doc_type if doc_type in DOC_TYPES else "Noi bo",
        "version": version, "status": status if status in DOC_STATUS else "Hieu luc",
        "attachment": attachment, "summary": summary, "location": location, "retention": retention,
    })
    _add_change(doc, "Tao moi")
    doc.insert()
    return {"name": doc.name}


FIELD_VI = {
    "doc_name": "Ten", "doc_code": "Ma", "version": "Phien ban", "summary": "Tom tat",
    "location": "Noi luu", "retention": "Thoi gian luu", "attachment": "Tep dinh kem",
    "content": "Noi dung", "doc_category": "Nhom", "doc_type": "Loai", "status": "Tinh trang",
}


@frappe.whitelist()
def update_document(name: str, doc_name: str = None, doc_code: str = None, doc_category: str = None,
                    doc_type: str = None, version: str = None, status: str = None,
                    attachment: str = None, summary: str = None, location: str = None,
                    retention: str = None, content: str = None, note: str = None) -> dict:
    """Cap nhat/soan tai lieu (chi quan ly QA) + ghi log thay doi. Sua xong -> Cho duyet."""
    _guard()
    doc = frappe.get_doc("Controlled Document", name)
    changes = []
    fields = {
        "doc_name": doc_name, "doc_code": doc_code, "version": version, "content": content,
        "summary": summary, "location": location, "retention": retention, "attachment": attachment,
    }
    if doc_category in DOC_CATS:
        fields["doc_category"] = doc_category
    if doc_type in DOC_TYPES:
        fields["doc_type"] = doc_type
    if status in DOC_STATUS:
        fields["status"] = status
    for f, v in fields.items():
        if v is not None and (doc.get(f) or "") != v:
            doc.set(f, v)
            changes.append(FIELD_VI.get(f, f))
    if not changes:
        return {"name": doc.name, "changed": []}
    # Co thay doi -> can phe duyet lai
    doc.approval_status = "Cho duyet"
    doc.signed_pdf = None
    summary_txt = ", ".join(changes)
    _add_change(doc, "Cap nhat", (note + " — " if note else "") + "Sua: " + summary_txt + " (cho duyet)")
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "changed": changes, "approval_status": doc.approval_status}


@frappe.whitelist()
def approve_document(name: str, signed_pdf: str, note: str = None) -> dict:
    """Phe duyet ban sua: bat buoc dinh kem ban PDF da ky (giam doc). Chi quan ly QA."""
    _guard()
    if not signed_pdf:
        frappe.throw(_("Can dinh kem ban PDF da ky cua giam doc de phe duyet"))
    doc = frappe.get_doc("Controlled Document", name)
    doc.approval_status = "Da duyet"
    doc.signed_pdf = signed_pdf
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    _add_change(doc, "Phe duyet", (note + " — " if note else "") + "Da phe duyet + tai ban ky (giam doc)")
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "approval_status": doc.approval_status, "signed_pdf": doc.signed_pdf}
