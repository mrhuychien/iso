"""Danh muc tai lieu ISO 22000 (Cong ty CP Hoang Giang).

Nguon: tai_lieu_iso/Lich cong viec & Danh muc bieu mau ATTP (cap nhat).xlsx
(sheet "Danh muc tai lieu noi bo" + "Danh muc bieu mau") va
tai_lieu_iso/Cap nhat phap luat ATTP 2026 - Danh muc tai lieu ben ngoai.html.

Ten/ma tai lieu giu nguyen TIENG VIET CO DAU (la noi dung hien thi, khong phai
fieldname/option). Nhom (doc_category) va trang thai (status) luu ASCII de khop
options Select. Seed idempotent theo doc_code.
"""
import os
import frappe
from frappe.utils import now_datetime

# Noi dung tai lieu (HTML) trich tu cac file .docx goc trong tai_lieu_iso/,
# luu trong setup/doc_content/<slug>.html. Map: doc_code -> slug.
CONTENT_FILES = {
    "QT.01": "qt_01", "QT.02": "qt_02", "QT.03": "qt_03", "QT.04": "qt_04", "QT.05": "qt_05",
    "QT.06": "qt_06", "QT.07": "qt_07", "QT.08": "qt_08", "QT.10": "qt_10", "QT.11": "qt_11", "QT.12": "qt_12",
    "MTATTP": "mtattp", "STATTP": "stattp", "SSOP / PRP": "ssop_prp",
    "KH.HACCP.01": "kh_haccp_01", "KH.HACCP.02": "kh_haccp_02", "QĐ.01": "qd_01",
    "KH.OPRP.01": "kh_oprp_01", "KH.KN.01": "kh_kn_01", "KH.SL.01": "kh_sl_01",
    "BM.PG.01": "bm_pg_01", "BM.02.03": "bm_02_03",
}
_CONTENT_DIR = os.path.join(os.path.dirname(__file__), "doc_content")


def _load_content(code):
    slug = CONTENT_FILES.get(code)
    if not slug:
        return None
    try:
        with open(os.path.join(_CONTENT_DIR, slug + ".html"), encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None

# Nhom (khop options doc_category trong Controlled Document)
G_POLICY = "Chinh sach - Muc tieu"
G_MANUAL = "So tay - PRP/SSOP"
G_PLAN = "Ke hoach (HACCP/OPRP/KN/SL)"
G_PROC = "Quy trinh (QT)"
G_RULE = "Quy dinh (QD)"
G_FORM = "Bieu mau - Ho so (BM)"
G_LIST = "Danh muc - Dinh muc"
G_EXT = "Tai lieu ben ngoai"

# (doc_code, doc_name, doc_category, doc_type, location, retention, summary)
CATALOG = [
    # --- Tai lieu noi bo: he thong ---
    ("CSATTP", "Chính sách an toàn thực phẩm", G_POLICY, "Noi bo", "", "", ""),
    ("MTATTP", "Mục tiêu an toàn thực phẩm", G_POLICY, "Noi bo", "", "", ""),
    ("STATTP", "Sổ tay an toàn thực phẩm", G_MANUAL, "Noi bo", "", "", ""),
    ("SSOP / PRP", "Hệ thống SSOP / Quy phạm vệ sinh PRP", G_MANUAL, "Noi bo", "", "", ""),
    ("KH.HACCP.01", "Kế hoạch HACCP bánh đậu xanh", G_PLAN, "Noi bo", "", "", ""),
    ("KH.HACCP.02", "Kế hoạch HACCP bột đậu", G_PLAN, "Noi bo", "", "", ""),
    ("KH.OPRP.01", "Kế hoạch OPRP & xác định CCP/OPRP", G_PLAN, "Noi bo", "", "", ""),
    ("KH.KN.01", "Kế hoạch kiểm nghiệm & giám sát môi trường", G_PLAN, "Noi bo", "", "", ""),
    ("KH.SL.01", "Kế hoạch thẩm định hạn sử dụng (shelf-life)", G_PLAN, "Noi bo", "", "", ""),
    ("QĐ.01", "Quy định lưu mẫu", G_RULE, "Noi bo", "", "", ""),
    ("QT.01", "QT Quản lý chung hệ thống ATTP", G_PROC, "Noi bo", "Ban ISO", "", ""),
    ("QT.02", "QT Thu hồi sản phẩm", G_PROC, "Noi bo", "Đội ATTP", "", ""),
    ("QT.03", "QT Ứng phó với tình huống khẩn cấp", G_PROC, "Noi bo", "Văn phòng", "", ""),
    ("QT.04", "QT Thẩm tra", G_PROC, "Noi bo", "Ban ISO", "", ""),
    ("QT.05", "QT Xác định bên quan tâm và rủi ro", G_PROC, "Noi bo", "Các bộ phận", "", ""),
    ("QT.06", "QT Quản lý thiết bị sản xuất và thiết bị đo", G_PROC, "Noi bo", "Phân xưởng SX", "", ""),
    ("QT.07", "QT Mua hàng, đánh giá lựa chọn nhà cung cấp", G_PROC, "Noi bo", "Kế toán", "", ""),
    ("QT.08", "QT Quản lý sản xuất", G_PROC, "Noi bo", "Phân xưởng SX", "", ""),
    ("QT.10", "QT Kiểm soát dị vật, thủy tinh–nhựa giòn, hóa chất và rework", G_PROC, "Noi bo", "Phân xưởng", "", ""),
    ("QT.11", "QT Phòng vệ thực phẩm (TACCP/VACCP)", G_PROC, "Noi bo", "Ban ISO", "", ""),
    ("QT.12", "QT Kiểm soát quy cách sản phẩm và ghi nhãn", G_PROC, "Noi bo", "Ban ISO", "", ""),
    ("BM.PG.01", "Bảng định mức phụ gia, phẩm màu", G_LIST, "Noi bo", "Ban ISO", "Lâu dài", ""),
    ("DM.NVL.01", "Danh mục quản lý nguyên vật liệu", G_LIST, "Noi bo", "Ban ISO/Mua hàng", "Lâu dài", ""),

    # --- Bieu mau / Ho so (BM) theo quy trinh ---
    ("BM.01.01", "Phiếu yêu cầu sửa đổi/ban hành tài liệu", G_FORM, "Noi bo", "Ban ISO", "2 năm", "QT01"),
    ("BM.01.02", "Danh mục tài liệu nội bộ", G_FORM, "Noi bo", "Các bộ phận", "Lâu dài", "QT01"),
    ("BM.01.03", "Danh mục tài liệu bên ngoài", G_FORM, "Noi bo", "Các bộ phận", "Lâu dài", "QT01"),
    ("BM.01.04", "Danh mục hồ sơ", G_FORM, "Noi bo", "Ban ISO", "Lâu dài", "QT01"),
    ("BM.01.05", "Chương trình và kế hoạch đánh giá", G_FORM, "Noi bo", "Ban ISO", "2 năm", "QT01"),
    ("BM.01.06", "Check list đánh giá", G_FORM, "Noi bo", "Ban ISO", "2 năm", "QT01"),
    ("BM.01.07", "Phiếu yêu cầu hành động khắc phục/phòng ngừa", G_FORM, "Noi bo", "Các bộ phận", "2 năm", "QT01"),
    ("BM.01.08", "Bảng tổng hợp các điểm lưu ý đánh giá", G_FORM, "Noi bo", "Ban ISO", "2 năm", "QT01"),
    ("BM.01.09", "Báo cáo đánh giá / tổng hợp kết quả", G_FORM, "Noi bo", "Ban ISO", "2 năm", "QT01"),
    ("BM.02.01", "Kế hoạch thu hồi sản phẩm", G_FORM, "Noi bo", "Đội ATTP", "2 năm", "QT02"),
    ("BM.02.02", "Báo cáo thu hồi sản phẩm", G_FORM, "Noi bo", "Đội ATTP", "2 năm", "QT02"),
    ("BM.02.03", "Biểu mẫu diễn tập thu hồi (mock recall)", G_FORM, "Noi bo", "Đội ATTP", "2 năm", "QT02"),
    ("BM.03.01", "Sổ quản lý thiết bị PCCC", G_FORM, "Noi bo", "KH-TH", "3 năm", "QT03"),
    ("BM.03.02", "Sổ theo dõi tình hình phát sinh dịch bệnh", G_FORM, "Noi bo", "KH-TH", "3 năm", "QT03"),
    ("BM.03.03", "Sổ quản lý thiết bị cần kiểm định an toàn", G_FORM, "Noi bo", "PX.SX", "3 năm", "QT03"),
    ("PL.03.01", "Phương án ứng phó bão lũ", G_FORM, "Noi bo", "Văn phòng", "Theo hiệu lực", "QT03"),
    ("PL.03.02", "Phương án chữa cháy", G_FORM, "Noi bo", "Văn phòng", "Theo hiệu lực", "QT03"),
    ("PL.03.03", "Phương án ứng phó rò điện/điện giật", G_FORM, "Noi bo", "Văn phòng", "Theo hiệu lực", "QT03"),
    ("PL.03.04", "Phương án phòng chống dịch bệnh", G_FORM, "Noi bo", "Văn phòng", "Theo hiệu lực", "QT03"),
    ("PL.03.05", "Phương án ứng phó thông tin sản phẩm", G_FORM, "Noi bo", "Văn phòng", "Theo hiệu lực", "QT03"),
    ("BM.04.01", "Kế hoạch thẩm tra", G_FORM, "Noi bo", "Ban ISO", "3 năm", "QT04"),
    ("BM.04.02", "Báo cáo / Phiếu thẩm tra", G_FORM, "Noi bo", "Ban ISO", "3 năm", "QT04"),
    ("BM.05.01", "Bảng xác định các bên quan tâm", G_FORM, "Noi bo", "Các bộ phận", "2 năm", "QT05"),
    ("BM.05.02", "Bảng xác định rủi ro và cơ hội", G_FORM, "Noi bo", "Các bộ phận", "2 năm", "QT05"),
    ("BM.06.01", "Danh mục thiết bị", G_FORM, "Noi bo", "Phân xưởng SX", "Lâu dài", "QT06"),
    ("BM.06.02", "Sổ theo dõi bảo dưỡng, sửa chữa thiết bị", G_FORM, "Noi bo", "Cơ điện", "3 năm", "QT06"),
    ("BM.06.03", "Biên bản hiệu chuẩn nội bộ thiết bị đo", G_FORM, "Noi bo", "Phân xưởng SX", "3 năm", "QT06"),
    ("BM.07.01", "Phiếu đánh giá nhà cung ứng", G_FORM, "Noi bo", "Kế toán", "2 năm", "QT07"),
    ("BM.07.02", "Danh sách nhà cung cấp được duyệt", G_FORM, "Noi bo", "Văn phòng", "2 năm", "QT07"),
    ("BM.07.03", "Sổ kiểm tra chất lượng hàng hóa nhập về", G_FORM, "Noi bo", "Kho/Kế toán", "2 năm", "QT07"),
    ("HD.07.01", "Hướng dẫn kế hoạch kiểm soát chất lượng vật tư, nguyên liệu", G_FORM, "Noi bo", "Kế toán/KCS", "Theo hiệu lực", "QT07"),
    ("PLK", "Phiếu theo dõi sản lượng sản xuất (phiếu lương CN)", G_FORM, "Noi bo", "Phần mềm", "2 năm", "QT08"),
    ("BCSX", "Báo cáo sản lượng sản xuất", G_FORM, "Noi bo", "Phần mềm", "2 năm", "QT08"),
    ("SLM", "Sổ theo dõi lưu mẫu", G_FORM, "Noi bo", "Văn phòng", "2 năm", "QĐ.01"),
    ("BM.10.01", "Sổ kiểm tra dị vật / lưới sàng / đầu dò", G_FORM, "Noi bo", "Phân xưởng", "2 năm", "QT10"),
    ("BM.10.02", "Danh mục thủy tinh – nhựa giòn", G_FORM, "Noi bo", "Phân xưởng", "Lâu dài", "QT10"),
    ("BM.10.03", "Biên bản xử lý vỡ thủy tinh/nhựa giòn", G_FORM, "Noi bo", "Phân xưởng", "2 năm", "QT10"),
    ("BM.10.04", "Danh mục hóa chất + SDS", G_FORM, "Noi bo", "Văn phòng/Phân xưởng", "Lâu dài", "QT10"),
    ("BM.10.05", "Sổ theo dõi hàng tái chế (rework)", G_FORM, "Noi bo", "Phân xưởng", "2 năm", "QT10"),
    ("BM.11.01", "Bảng đánh giá mối đe dọa & lỗ hổng (TACCP/VACCP)", G_FORM, "Noi bo", "Ban ISO", "Lâu dài", "QT11"),
    ("BM.12.01", "Bản quy cách sản phẩm (specification)", G_FORM, "Noi bo", "Ban ISO", "Lâu dài", "QT12"),
    ("BM.12.02", "Phiếu kiểm tra & phê duyệt nhãn", G_FORM, "Noi bo", "Văn phòng/Ban ISO", "2 năm", "QT12"),
    ("BM.12.03", "Hồ sơ xử lý sai nhãn", G_FORM, "Noi bo", "Phân xưởng", "2 năm", "QT12"),
    ("VSCN", "Sổ kiểm tra vệ sinh công nhân hàng ngày", G_FORM, "Noi bo", "SX", "2 năm", "PRP"),
    ("VSCT", "Báo cáo tình hình vệ sinh công ty", G_FORM, "Noi bo", "SX", "2 năm", "PRP"),
    ("VSDK", "Báo cáo vệ sinh định kỳ", G_FORM, "Noi bo", "SX", "2 năm", "PRP"),
    ("KTTP", "Sổ theo dõi kiểm tra thành phẩm", G_FORM, "Noi bo", "SX", "2 năm", "KH HACCP"),

    # --- Tai lieu ben ngoai: phap luat & tieu chuan (ra soat 14/06/2026) ---
    ("55/2010/QH12", "Luật An toàn thực phẩm", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Hiện hành (đang sửa đổi). Khung pháp lý ATTP."),
    ("15/2018/NĐ-CP", "NĐ quy định chi tiết thi hành Luật ATTP (tự công bố/đăng ký SP)", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Sửa bởi 155/2018/NĐ-CP. Đang dự thảo sửa đổi."),
    ("115/2018/NĐ-CP", "NĐ xử phạt VPHC về ATTP", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Sửa bởi 124/2021/NĐ-CP. Hiện hành."),
    ("111/2021/NĐ-CP", "NĐ về nhãn hàng hóa (sửa NĐ 43/2017)", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Hiệu lực 15/02/2022. Ghi nhãn, công bố thành phần/allergen."),
    ("24/2019/TT-BYT", "TT quản lý & sử dụng phụ gia thực phẩm", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Sửa bởi 17/2023, 08/2024; hợp nhất 09/VBHN-BYT/2024 — dùng bản hợp nhất 2024."),
    ("15/2024/TT-BYT", "TT danh mục thực phẩm/phụ gia/bao bì kèm mã HS kiểm tra NN khi nhập khẩu", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Hiện hành. Liên quan QT07 (mua hàng/nhập khẩu)."),
    ("QCVN 8-1:2011/BYT", "QCVN giới hạn ô nhiễm độc tố vi nấm (aflatoxin)", G_EXT, "Ben ngoai", "Ban ISO/KCS", "Theo hiệu lực", "Giới hạn aflatoxin đỗ/lạc. Liên quan KH.OPRP.01, KH.KN.01."),
    ("QCVN 8-2:2011/BYT", "QCVN giới hạn ô nhiễm kim loại nặng", G_EXT, "Ben ngoai", "Ban ISO/KCS", "Theo hiệu lực", "Pb, As, Cd, Hg trong thực phẩm. Liên quan KH.KN.01."),
    ("QCVN 8-3:2012/BYT", "QCVN giới hạn ô nhiễm vi sinh vật", G_EXT, "Ben ngoai", "Ban ISO/KCS", "Theo hiệu lực", "Chỉ tiêu vi sinh thành phẩm. Liên quan KH.KN.01."),
    ("QCVN 01-1:2024/BYT", "QCVN chất lượng nước sạch sinh hoạt", G_EXT, "Ben ngoai", "Ban ISO/KCS", "Theo hiệu lực", "Nước sản xuất. Liên quan PRP–SSOP1, KH.KN.01."),
    ("02/2024/TT-BKHCN", "TT quản lý truy xuất nguồn gốc sản phẩm, hàng hóa", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Nguyên tắc, dữ liệu truy xuất. Liên quan QT02."),
    ("TCVN 7240:2003", "TCVN Bánh đậu xanh", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Tiêu chuẩn áp dụng. Liên quan Kế hoạch HACCP, KH.KN.01."),
    ("TCVN 5603:2008", "TCVN Quy phạm thực hành vệ sinh thực phẩm (CAC/RCP 1-1969)", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "GHP/PRP. Liên quan PRP, QT08."),
    ("09/2016/NĐ-CP", "NĐ tăng cường vi chất dinh dưỡng vào thực phẩm", G_EXT, "Ben ngoai", "Ban ISO", "Theo hiệu lực", "Muối dùng trong chế biến (nếu áp dụng). Liên quan QT07."),
]


def ensure_documents():
    """Seed danh muc tai lieu ISO vao Controlled Document (idempotent theo doc_code).

    Tai lieu nao co file noi dung (.docx goc) thi nap luon vao truong content;
    voi ban ghi da ton tai nhung content con trong thi backfill (cap nhat nguoc).
    """
    user = frappe.session.user or "Administrator"
    for (code, name, cat, dtype, location, retention, summary) in CATALOG:
        content = _load_content(code)
        existing = frappe.db.get_value("Controlled Document", {"doc_code": code}, "name") if code else None
        if existing:
            if content:
                doc = frappe.get_doc("Controlled Document", existing)
                if not (doc.content or "").strip():
                    doc.content = content
                    doc.append("change_log", {
                        "changed_on": now_datetime(), "changed_by": user,
                        "action": "Nhap noi dung", "version": doc.version or "",
                        "note": "Trich noi dung tu tai lieu goc (.docx)",
                    })
                    doc.save(ignore_permissions=True)
            continue
        doc = frappe.get_doc({
            "doctype": "Controlled Document", "doc_name": name, "doc_code": code,
            "doc_category": cat, "doc_type": dtype, "status": "Hieu luc",
            "location": location or None, "retention": retention or None,
            "summary": summary or None, "content": content,
            "change_log": [{
                "changed_on": now_datetime(), "changed_by": user,
                "action": "Nhap danh muc ISO", "version": "",
                "note": "Khoi tao tu danh muc chuan" + (" + noi dung tai lieu" if content else ""),
            }],
        })
        doc.insert(ignore_permissions=True)
