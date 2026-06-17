frappe.ui.form.on("OPRP Monitoring Log", {
  batch_no(frm) {
    // Tu dong lay Work Order tu Batch (neu co lien ket)
    if (frm.doc.batch_no && !frm.doc.work_order) {
      frappe.db.get_value("Batch", frm.doc.batch_no, "reference_name").then((r) => {
        if (r && r.message && r.message.reference_name) {
          frm.set_value("work_order", r.message.reference_name);
        }
      });
    }
  },
});
