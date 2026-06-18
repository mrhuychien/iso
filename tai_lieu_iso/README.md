# Tài liệu ISO 22000 — Công ty CP Hoàng Giang

Bộ quy trình + biểu mẫu hệ thống ATTP, kèm theo các deliverable đã chuẩn hóa.
(Đây là nguồn nghiệp vụ cho app `hg_food_safety`; không phải code.)

## Cấu trúc
- `Hệ thống quy trình/` — bộ gốc: QT01–QT08, Sổ tay ATTP, Quy phạm vệ sinh PRP, Kế hoạch HACCP, QĐ.01 lưu mẫu, các biểu mẫu BM.* kèm theo.
- `Hệ thống quy trình (đã sửa)/` — bản đã rà soát/chuẩn hóa (QT01–QT08, PRP, HACCP, Sổ tay…); SSOP1 kiểm soát nước đã cập nhật.
- `Hệ thống quy trình (bổ sung)/` — quy trình bổ sung QT10/QT11/QT12, các kế hoạch KH.OPRP/KH.KN/KH.SL, **Bảng định mức phụ gia (BM.PG.01)**, **Danh mục quản lý nguyên vật liệu (DM.NVL.01)**, biểu mẫu mock recall. (QT09 Allergen đã loại bỏ.)

## Deliverable đã chuẩn hóa (file rời)
- `Bo bieu mau chuan hoa ATTP (san sang so hoa).xlsx` — 45 biểu mẫu chuẩn hóa, sẵn sàng số hóa (1 sheet = 1 bảng dữ liệu).
- `Lich cong viec & Danh muc bieu mau ATTP (cap nhat).xlsx` — lịch công việc + danh mục biểu mẫu hợp nhất + danh mục tài liệu nội bộ (đã sửa mâu thuẫn).
- `Lich cong viec ATTP Hoang Giang.xlsx` — lịch công việc gốc.
- `Noi quy an toan ve sinh thuc pham.docx` — nội quy ATVSTP để ban hành.
- `Huong dan su dung bieu mau (cho nguoi moi).docx` — hướng dẫn từng biểu mẫu.
- `Ra soat bieu mau - quy trinh (danh gia & cai tien).xlsx` — rà soát 48 biểu mẫu + đề xuất cải tiến.
- `Bang_tong_hop_thay_doi_tai_lieu.xlsx` — tổng hợp thay đổi tài liệu.
- `Ban mo ta thiet ke - He thong ATTP so hoa tren ERPNext v16.md` — blueprint thiết kế app (6 phần) + mapping 45 biểu mẫu.
- `Prompt thiet ke giao dien (Google Stitch).md` — prompt thiết kế UI.
- Các file `.html` — danh mục tài liệu bên ngoài / báo cáo phụ trợ.

## Không kèm trong repo (giữ ở máy)
- `TỰ CÔNG BỐ/` (PDF bản tự công bố ~25MB) và `2025/` (hồ sơ thực thi theo năm). Bổ sung sau nếu cần.

## Ánh xạ biểu mẫu → app
Xem `../HANDOVER.md` và `Ban mo ta thiet ke ...md` (Phụ lục A) để biết mỗi biểu mẫu được số hóa thành DocType nào trong `hg_food_safety`.
