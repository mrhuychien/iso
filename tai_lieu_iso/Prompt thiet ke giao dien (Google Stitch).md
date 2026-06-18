# Prompt thiết kế giao diện cho Google Stitch — Portal ATTP Hoàng Giang

Cách dùng: trong Stitch chọn chế độ **Mobile**, dán **Prompt 0 (hệ thống)** trước để khoá phong cách, rồi dán lần lượt từng prompt màn hình (1 → 4). Nếu Stitch hiểu tiếng Việt chưa tốt, dùng phần “English version” ở cuối.

---

## PROMPT 0 — Hệ thống / phong cách (dán đầu tiên)

Thiết kế một ứng dụng web mobile-first tên “ATTP Hoàng Giang” — phần mềm quản lý an toàn thực phẩm (ISO 22000) cho một nhà máy sản xuất bánh đậu xanh. Người dùng là nhân viên KCS và quản lý QA, thao tác chủ yếu trên điện thoại và máy tính bảng đặt tại bàn kiểm soát chất lượng.

Phong cách: hiện đại, sạch sẽ, chuyên nghiệp, thân thiện nhưng nghiêm túc. Phẳng (flat) với đổ bóng rất nhẹ, bo góc lớn 14–16px, nhiều khoảng trắng. Mọi chữ bằng tiếng Việt có dấu.

Hệ màu: màu chính xanh lá thực phẩm #16A34A và xanh đậm #15803D; nền tổng thể xám rất nhạt #F6F8FA; thẻ nền trắng; chữ xám đậm #0F172A, chữ phụ #64748B; cảnh báo đỏ #DC2626 trên nền #FEF2F2; trạng thái tốt nền #ECFDF5. Font sans-serif (Inter/SF Pro), tiêu đề đậm, body 14–16px, nút và ô nhập cỡ chạm lớn (cao ~44px).

Bố cục chung mọi màn hình: thanh tiêu đề trên cùng màu xanh lá chứa logo nhỏ “ATTP” + “Hoàng Giang” bên trái và tên người dùng bên phải; nội dung ở giữa dạng thẻ; **thanh điều hướng cố định dưới đáy** gồm 3 mục có icon: “Hôm nay”, “Truy xuất lô”, “Bảng điều khiển” (mục đang chọn tô xanh đậm).

---

## PROMPT 1 — Màn hình “Hôm nay” (trang chủ)

Màn hình chính “Hôm nay” của app ATTP Hoàng Giang.
- Trên cùng: thanh tiêu đề xanh lá (logo “ATTP” + “Hoàng Giang”, tên người dùng góc phải).
- Ngay dưới: một banner cảnh báo màu đỏ bo góc: “2 lô đang bị cô lập — cần xử lý”.
- Tiêu đề mục “Ghi nhanh”.
- Lưới thẻ hành động 2 cột: mỗi thẻ nền trắng bo góc, có một icon tròn nền xanh nhạt phía trên và nhãn đậm bên dưới. Các thẻ: “Giám sát OPRP”, “Kiểm dị vật”, “Kết quả kiểm nghiệm”, “Lưu mẫu”, “Nhật ký vệ sinh”, “Kiểm soát nước”, “Hàng tái chế”.
- Tiêu đề mục “Đã ghi hôm nay”.
- Hàng 4 thẻ số liệu nhỏ: mỗi thẻ một con số lớn màu xanh đậm và nhãn nhỏ bên dưới (“Giám sát OPRP 3”, “Kiểm dị vật 5”, “Nhật ký vệ sinh 2”, “Kiểm soát nước 1”).
- Dưới đáy: thanh điều hướng 3 mục (Hôm nay đang chọn).

---

## PROMPT 2 — Màn hình form nhập “Giám sát OPRP”

Màn hình nhập liệu “Giám sát OPRP” trong app ATTP.
- Trên cùng: liên kết “← Quay lại” và tiêu đề “Giám sát OPRP”.
- Form dọc, mỗi trường có nhãn đậm phía trên, ô nhập bo góc cỡ lớn:
  - “Ngày” (ô chọn ngày), “Ca” (dropdown: Sáng/Chiều/Tối).
  - “Lô (Batch)” (ô tìm kiếm có gợi ý thả xuống), “Người giám sát” (ô tìm kiếm).
  - Bảng con “Chi tiết giám sát” gồm các cột: OPRP/Công đoạn, Thông số, Giới hạn hành động, Kết quả, Trạng thái (dropdown Đạt/Không đạt), và nút xoá dòng (×); bên dưới bảng có nút phụ “+ Thêm dòng”.
  - Ô nhiều dòng “Hành động khắc phục (nếu vượt giới hạn)”.
- Dưới cùng: một nút lớn full-width màu xanh lá “Lưu & gửi”.
- Vẫn có thanh điều hướng đáy.

---

## PROMPT 3 — Màn hình “Truy xuất lô”

Màn hình “Truy xuất theo lô” trong app ATTP.
- Tiêu đề “Truy xuất theo lô”.
- Một hàng gồm ô nhập “Nhập mã lô (Batch)” và nút xanh “Truy xuất”.
- Banner trạng thái lô (màu xanh nếu Đạt, đỏ nếu Cô lập): “Trạng thái lô: Đang cô lập”.
- Nhiều nhóm dạng dòng thời gian (timeline), mỗi nhóm có tiêu đề kèm một badge tròn số lượng: “Giám sát OPRP (3)”, “Kiểm dị vật (2)”, “Kiểm thành phẩm (1)”, “Lưu mẫu (1)”. Trong mỗi nhóm là các dòng thẻ nhỏ: bên trái mã bản ghi (kiểu chữ monospace màu xanh), bên phải chi tiết ngày/ca/kết quả màu xám.
- Thanh điều hướng đáy (Truy xuất lô đang chọn).

---

## PROMPT 4 — Màn hình “Bảng điều khiển” (cho QA)

Màn hình “Bảng điều khiển ATTP” dành cho quản lý.
- Tiêu đề “Bảng điều khiển ATTP”.
- Mục “Cảnh báo”: lưới 4 thẻ số liệu — “Lô đang cô lập” (thẻ nền đỏ nhạt, số đỏ), “Sự không phù hợp”, “Mẫu đến hạn hủy”, “Hiệu chuẩn < 30 ngày”.
- Mục “KPI 30 ngày”: 3 thẻ số liệu — “% đạt thành phẩm”, “% OPRP vượt”, “Mock recall (giờ)”.
- Mục “Ghi nhận hôm nay”: một biểu đồ cột trong thẻ trắng, 4 cột xanh lá (OPRP, Thành phẩm, Dị vật, Vệ sinh).
- Thanh điều hướng đáy (Bảng điều khiển đang chọn).

---

## English version (nếu Stitch hiểu tiếng Việt chưa tốt — phần style, dịch các nhãn sang tiếng Việt sau)

Design a mobile-first web app called “ATTP Hoang Giang”, a food-safety (ISO 22000) management tool for a mung-bean-cake factory, used by QC and QA staff on phones/tablets. Style: modern, clean, professional, flat with very subtle shadows, large 14–16px rounded corners, generous whitespace. Primary color food-safety green #16A34A / #15803D; page background #F6F8FA; white cards; text #0F172A and muted #64748B; danger red #DC2626 on #FEF2F2; success #ECFDF5. Sans-serif (Inter), bold headings, large 44px touch inputs. Every screen has: a green top header (logo “ATTP” + company + user) and a fixed bottom navigation with three icon tabs (Today, Batch trace, Dashboard). Screens: (1) Today — red alert banner, “Quick entry” grid of icon action cards, “Logged today” stat cards; (2) entry form with date, dropdown, searchable link fields, an editable child-row table with “add row”, and a full-width green save button; (3) Batch trace — search bar, batch-status banner, timeline sections with count badges; (4) Dashboard — alert stat cards (isolated batches in red), 30-day KPI cards, and a green bar chart. Keep all visible labels in Vietnamese (with diacritics).
