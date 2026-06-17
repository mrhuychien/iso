app_name = "hg_food_safety"
app_title = "Food Safety"
app_publisher = "Hoang Giang JSC"
app_description = "He thong an toan thuc pham (ISO 22000) tich hop module Quality - ERPNext v16"
app_email = "info@rongvanghoanggia.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# ═══════════════════════════════════════════════════════════════
# DocType Events
# ═══════════════════════════════════════════════════════════════
doc_events = {
    "Quality Inspection": {
        "on_submit": "hg_food_safety.api.qc.on_inspection_submit",
    },
    "OPRP Monitoring Log": {
        "validate": "hg_food_safety.api.oprp.compute_deviation",
        "on_submit": "hg_food_safety.api.oprp.handle_deviation",
    },
    "Foreign Body Check Log": {
        "on_submit": "hg_food_safety.api.fbc.handle_fail",
    },
    "Stock Entry": {
        "on_submit": "hg_food_safety.api.batch.init_finished_batch",
    },
    "Doc Change Request": {
        "on_update_after_submit": "hg_food_safety.api.docs.apply_version",
    },
}

# ═══════════════════════════════════════════════════════════════
# Scheduled Tasks
# ═══════════════════════════════════════════════════════════════
scheduler_events = {
    "daily": [
        "hg_food_safety.tasks.remind_sample_disposal",
        "hg_food_safety.tasks.remind_calibration_due",
        "hg_food_safety.tasks.remind_lab_test_due",
    ],
}

# ═══════════════════════════════════════════════════════════════
# Portal SPA (www page tu render; route ngan gon)
# ═══════════════════════════════════════════════════════════════
website_route_rules = [
    {"from_route": "/atp/<path:app_path>", "to_route": "atp"},
]

# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════
fixtures = [
    {"doctype": "Role", "filters": [["name", "in", ["FS QC", "FS QA Manager"]]]},
    {
        "doctype": "Custom Field",
        "filters": [["name", "in", [
            "Batch-custom_qc_status", "Batch-custom_qc_hold", "Batch-custom_oprp_ok",
            "Item-custom_fs_category", "Item-custom_storage_condition",
            "Item-custom_qc_required_docs", "Item-custom_legal_basis",
            "Supplier-custom_approved", "Supplier-custom_reeval_date",
        ]]],
    },
    {"doctype": "Property Setter", "filters": [["module", "=", "Food Safety"]]},
    {"doctype": "Workflow", "filters": [["name", "in", [
        "Product Recall Workflow", "Doc Change Request Workflow", "Label Approval Workflow"]]]},
    {"doctype": "Workflow State", "filters": [["name", "in", [
        "Nhap", "Dang thu hoi", "Cho phe duyet dong", "Da dong",
        "Cho duyet", "Da duyet", "Tu choi"]]]},
    {"doctype": "Workflow Action Master", "filters": [["name", "in", [
        "Phat lenh", "Hoan tat", "Phe duyet", "Tu choi", "Gui duyet"]]]},
    {"doctype": "Print Format", "filters": [["module", "=", "Food Safety"]]},
]
