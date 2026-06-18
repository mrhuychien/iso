# BÀN GIAO — App ATTP `hg_food_safety` (ERPNext v16)

Tài liệu cho dev/AI tiếp nhận (Claude Code) làm tiếp. Đọc hết phần này trước khi sửa code.

## 1. Bối cảnh
- App quản lý An toàn thực phẩm (ISO 22000) cho Công ty CP Hoàng Giang (sản xuất bánh đậu xanh, bột đậu).
- Tích hợp vào **module Quality + Manufacturing/Batch** của ERPNext v16 có sẵn.
- Người dùng thật chỉ 2: **KCS** (role `FS QC`) và **QA/anh chủ** (role `FS QA Manager` + `System Manager`).
- Build theo "kiểu NPP": backend Python whitelisted-method có guard, DocType chuẩn + Custom Field qua fixtures/setup, portal SPA no-build, fieldname ASCII.

## 2. Repo & deploy
- Git: `https://github.com/mrhuychien/iso.git`, nhánh `main`.
- Cài trên bench (site DEV, backup trước):
  ```bash
  bench get-app https://github.com/mrhuychien/iso.git   # hoặc copy vào apps/
  bench --site <site> install-app hg_food_safety
  bench --site <site> migrate          # tạo DocType + after_migrate seed Role/Custom Field/Workflow/ATTP Task
  bench build --app hg_food_safety
  bench --site <site> clear-cache && bench restart
  ```
- Portal: `https://<site>/atp` (đăng nhập user có role `FS QC` hoặc `FS QA Manager`).
- **Thứ tự bắt buộc khi đổi code: migrate → build → restart → refresh.**

## 3. Đã build (trạng thái: chạy được, cần nghiệm thu trên bench)
- **40 DocType** trong module Food Safety (parent + child). Chính: OPRP Monitoring Log (+OPRP Reading), Foreign Body Check Log, Sample Retention, Sanitation Log (+item), Water Control Log, Rework Log, Environmental Monitoring, Lab Test Result, Glass Brittle Register (+item), Breakage Incident, Chemical Register, Food Defense Assessment (+Threat Item), Product Specification, Additive Dosage Spec (+row), Label Approval (+checklist), Periodic Sanitation Log, Product Recall (+Recall Step), Internal Audit (+finding), Verification Record (+item), Risk Register, Interested Party, Emergency Record, Fire Equipment Log (+item), Calibration Record, Controlled Document (+attachment/summary), Doc Change Request, Shelf Life Study (+reading), **ATTP Task**, **ATTP Task Log**.
- **Backend** `hg_food_safety/api/` (11 module): `_guards.py` (`_guard` quản lý, `require_fs`), `analytics.py` (dashboard_summary, qc_kpis — role-gated), `portal.py` (today_tasks, mark_task_done, create_record, search_link, documents, create_document), `trace.py` (by_batch), `recall.py`, `oprp.py/fbc.py/qc.py/batch.py/docs.py` (tự động hóa qua hooks).
- **Tự động hóa (hooks doc_events)**: OPRP vượt giới hạn / đầu dò "Bao" / Quality Inspection "Rejected" → cô lập Batch (`custom_qc_hold=1`, `custom_qc_status='Co lap'`) + tạo Non Conformance. Doc Change Request duyệt → cập nhật phiên bản Controlled Document. Stock Entry (Manufacture) → set trạng thái ATTP cho Batch.
- **Workflow theo lịch công việc**: `ATTP Task` (master, seed ~27 việc từ lịch ATTP) + `ATTP Task Log` (lần thực hiện). `schedule.py:generate_task_logs` sinh log theo `period_key` (mỗi ca/ngày/15 ngày/tháng/quý/6 tháng/năm), đánh dấu "Tre" khi qua kỳ. `portal.today_tasks` **tự seed + tự sinh log khi mở trang** (self-healing) → checklist luôn hiện việc chưa làm. Tạo bản ghi qua portal `create_record` **tự đánh dấu** task log có `linked_doctype` trùng.
- **Tài liệu nội bộ**: Controlled Document + `attachment`. Portal tab "Tài liệu": liệt kê + "Đọc" (mở file online), QA upload (upload_file → create_document). File đang để **public (is_private=0)**.
- **Portal SPA** `/atp` (`public/atp/`): shell.js (hash router, import-map cache-bust), views: home (checklist), entry (form nhập 7 biểu mẫu + link autocomplete + child table), trace, dashboard, documents. Giao diện **Material 3** (xanh #006b2c, Inter, Material Symbols) theo thiết kế Stitch; chữ tiếng Việt **có dấu**, giá trị lưu DB **không dấu** (khớp options/controller).
- **Workflow Frappe** (patch idempotent `create_workflows`): Product Recall, Doc Change Request, Label Approval.
- **Setup** đặt ở `setup/install.py` chạy qua `after_install` + `after_migrate` (KHÔNG dựa patches.txt — xem gotcha §5): ensure_roles, ensure_custom_fields, ensure_workflows, ensure_tasks.
- **Dịch**: `translations/vi.csv` (tên DocType → tiếng Việt không dấu).

## 4. QUY ƯỚC PHẢI GIỮ (kiểu NPP)
- Backend = file Python whitelisted method; **mỗi method gọi guard ở dòng đầu** (`_guard()` cho quản lý, `require_fs()` cho cả 2 vai). KHÔNG dùng Server/Client Script rải rác.
- **Fieldname/options lưu DB = ASCII không dấu**; nhãn hiển thị có dấu (qua label + vi.csv + label trong form portal).
- DocType chuẩn + Custom Field; chỉ tạo DocType mới khi cần.
- Portal: shared module mới phải thêm vào **import map** trong `www/atp.html`; view động dùng `?v=assetVersion`; CSS prefix `app-`.
- Verify trước commit: `python3 -m py_compile` toàn bộ .py + `node --check` toàn bộ .js + JSON hợp lệ + `field_order == fields`. Commit-per-feature.

## 5. GOTCHA ĐÃ DÍNH (đừng lặp lại)
1. `patches.txt` **phải có cả** `[pre_model_sync]` và `[post_model_sync]` (Frappe parser KeyError nếu thiếu).
2. **Fresh install bỏ qua patch** (đánh dấu hoàn thành mà không chạy) → setup mặc định (role/custom field/workflow/task) đặt ở `after_install`+`after_migrate`, KHÔNG ở patch.
3. CSRF cho portal: lấy an toàn (`frappe.sessions.get_csrf_token()` có fallback); api.js ưu tiên `frappe.csrf_token` global.
4. Method đụng custom field (vd `custom_qc_hold`) phải guard `frappe.db.has_column(...)` để không 500 khi field chưa tạo.
5. Checklist "toàn 0" do scheduler chưa chạy → đã xử lý bằng self-heal trong `today_tasks` (tự seed + sinh log khi mở trang).

## 6. CHƯA LÀM / VIỆC TIẾP THEO (đề xuất ưu tiên)
1. **Quality Inspection Template** (fixtures) cho "KT NVL nhập" (kèm aflatoxin lạc/đậu) và "KT thành phẩm" — hiện chỉ hook xử lý Rejected, chưa có template sẵn.
2. **Print Format** (BM thu hồi, KT thành phẩm, OPRP, quy cách SP…) — chưa tạo.
3. **Workspace "Food Safety"** + **Number Card / Dashboard Chart** desk cho QA (hiện chỉ có dashboard trên portal).
4. **Tệp tài liệu private**: hiện public; nếu cần bảo mật → đổi `is_private=1` + gắn quyền theo Controlled Document.
5. **Self-host font** Inter + Material Symbols vào `public/` nếu mạng nhà máy chặn Google Fonts.
6. **Test** (`nextcode-qa`): FrappeTestCase cho cô lập lô khi reject, `recovery_pct` (Product Recall), enforce like-into-like (Rework), generate_task_logs idempotent, apply_version (Doc Change).
7. Thêm form portal cho các DocType khác nếu cần nhập ngoài Desk; bổ sung tab/tinh chỉnh giao diện theo Stitch.
8. Cân nhắc Quality Inspection vào danh sách `ALLOWED_CREATE`/form portal nếu muốn KCS nhập KT thành phẩm ngay trên portal (hiện đang trỏ Desk/Lab form).

## 7. Test nhanh sau cài
1. Gán role: KCS → `FS QC`; QA → `FS QA Manager` + `System Manager`.
2. Tạo Item thành phẩm (Has Batch No) + 1 Batch.
3. `/atp` → Hôm nay: checklist hiện việc theo lịch (Chờ/Trễ). Bấm "Ghi" ở OPRP → nhập → Submit → lô tự cô lập nếu "Không đạt" + tạo Non Conformance + task tự đánh dấu đã làm.
4. Tab Tài liệu: QA upload 1 PDF → mọi người bấm "Đọc" xem online.
5. Dashboard (QA): cảnh báo lô cô lập + KPI + biểu đồ.

## 8. Tài liệu thiết kế kèm theo (trong thư mục ISO22000, ngoài repo app)
- `Ban mo ta thiet ke - He thong ATTP so hoa tren ERPNext v16.md` — blueprint 6 phần + mapping 45 biểu mẫu + kịch bản 2 người dùng.
- `giaodien/` (trong repo) — export thiết kế Material 3 từ Google Stitch (HTML + ảnh) làm tham chiếu giao diện.
