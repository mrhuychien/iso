# hg_food_safety — Hệ thống An toàn thực phẩm (ISO 22000) trên ERPNext v16

Custom app build **kiểu NPP** (nextcode + frappe-portal-spa + frappe-sales-analytics
+ shipping-gotchas): backend Python whitelisted-method có guard, DocType chuẩn + Custom
Field qua fixtures, **portal SPA no-build**, analytics role-gated. Tích hợp module
**Quality + Manufacturing/Batch**. Người dùng phần mềm: **KCS** (`FS QC`) và **QA** (`FS QA Manager`).

## Thành phần đã build (full theo blueprint)
- **38 DocType** module Food Safety (28 parent + 10 child), fieldname ASCII.
  - Ghi nhận theo lô: OPRP Monitoring Log, Foreign Body Check Log, Sample Retention,
    Sanitation Log, Water Control Log, Rework Log, Environmental Monitoring, Lab Test Result.
  - Kiểm soát mối nguy: Glass & Brittle Register, Breakage Incident, Chemical Register,
    Food Defense Assessment (TACCP/VACCP).
  - Hệ thống/tài liệu: Internal Audit, Verification Record, Risk Register, Interested Party,
    Controlled Document, Doc Change Request, Calibration Record, Emergency Record, Fire Equipment Log.
  - Sản phẩm/nhãn: Product Specification, Additive Dosage Spec, Label Approval.
  - Thu hồi: Product Recall (+ mock recall).
- **Backend** (`api/`): `_guards.py` (`_guard` quản lý, `require_fs`), `analytics.py`
  (dashboard_summary, qc_kpis — role-gated), `trace.py` (truy xuất theo lô), `recall.py`
  (prefill từ Stock Ledger), `oprp/fbc/qc/batch/docs.py` (tự động hóa qua hooks).
- **Portal SPA** tại `/atp` (frappe-portal-spa): import-map cache-bust, hash router,
  CSS prefix `app-`, Chart.js lazy. View: Hôm nay · Truy xuất lô · Dashboard (manager).
- **Tự động hóa**: OPRP vượt giới hạn / đầu dò báo / Quality Inspection Rejected →
  cô lập Batch + tạo Non Conformance. Doc Change Request duyệt → cập nhật phiên bản tài liệu.
  Scheduler nhắc hủy mẫu / hiệu chuẩn.
- **Workflow** (patch idempotent): Product Recall, Doc Change Request, Label Approval.
- **Custom Field** (fixtures): Batch (qc_status/qc_hold/oprp_ok), Item (fs_category/storage/
  required_docs/legal_basis), Supplier (approved/reeval_date).

## Trạng thái verify (đã chạy)
- 38/38 JSON hợp lệ, field_order khớp fields.
- 99 file Python `py_compile` OK; 8 file JS `node --check` OK.
- Mọi module có `__init__.py`.
- *Chưa* chạy trên bench thật (môi trường này không có Frappe) → cài lên site DEV để nghiệm thu.

## CÀI ĐẶT (chạy trên frappe-bench/, dùng site DEV — backup trước)
```bash
cp -r hg_food_safety $PATH_TO_BENCH/apps/         # hoặc bench get-app <git-url>
cd $PATH_TO_BENCH
bench --site <site-dev> backup
bench --site <site-dev> install-app hg_food_safety
bench --site <site-dev> migrate                   # tạo DocType + chạy patch (role, custom field, workflow)
bench build --app hg_food_safety                  # đẩy JS/CSS portal ra /assets
bench restart                                     # nạp lại Python (www context + method)
# rồi mở: https://<site>/atp  (đăng nhập user có role FS QC hoặc FS QA Manager)
```
Thứ tự **migrate → build → restart → refresh** là bắt buộc (xem skill shipping-gotchas).

## TEST NHANH
1. Gán role `FS QC` cho KCS, `FS QA Manager` (+ System Manager) cho QA.
2. Tạo Item thành phẩm `Has Batch No`, tạo Batch (vd HG-20260616-01).
3. OPRP Monitoring Log → 1 reading "Khong dat" → Submit → Batch chuyển "Co lap" + có Non Conformance.
4. Foreign Body Check Log → đầu dò "Bao" → Submit → lô cô lập.
5. Mở `/atp`: tab Hôm nay (việc đã ghi), Truy xuất lô (gõ mã lô), Dashboard (QA: cảnh báo + KPI + biểu đồ).

## Phân quyền
- `FS QC` (KCS): tạo/ghi/submit log; **không** xóa, **không** duyệt giải phóng/đóng recall.
- `FS QA Manager` (QA): toàn quyền + duyệt workflow + đóng CAPA/recall. Gán kèm `System Manager`.

## Lưu ý
- Kiểm tra NVL nhập / thành phẩm dùng **Quality Inspection (core)** + Template (tạo ở Desk
  hoặc bổ sung fixture sau) — app đã hook xử lý Rejected → cô lập lô.
- Print Format, Number Card/Dashboard Chart desk: chưa tạo (bổ sung khi nghiệm thu).
- Đây là bản build đầu để cài lên DEV và iterate; tinh chỉnh field/nhãn theo phản hồi thực tế.
