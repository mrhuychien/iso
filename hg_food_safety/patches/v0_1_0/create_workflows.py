"""Tao Workflow cho Product Recall, Doc Change Request, Label Approval. Idempotent."""
import frappe


def _ensure_states(states):
    for s in states:
        if not frappe.db.exists("Workflow State", s):
            frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": s}).insert(ignore_permissions=True)


def _ensure_actions(actions):
    for a in actions:
        if not frappe.db.exists("Workflow Action Master", a):
            frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": a}).insert(ignore_permissions=True)


def _make(workflow_name, doctype, states, transitions):
    if frappe.db.exists("Workflow", workflow_name):
        return
    doc = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": doctype,
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        "states": states,
        "transitions": transitions,
    })
    doc.insert(ignore_permissions=True)


def execute():
    _ensure_states(["Nhap", "Dang thu hoi", "Cho phe duyet dong", "Da dong",
                    "Cho duyet", "Da duyet", "Tu choi"])
    _ensure_actions(["Phat lenh", "Hoan tat", "Phe duyet", "Tu choi", "Gui duyet"])

    _make("Product Recall Workflow", "Product Recall",
        states=[
            {"state": "Nhap", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Dang thu hoi", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Cho phe duyet dong", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Da dong", "doc_status": "1", "allow_edit": "FS QA Manager"},
        ],
        transitions=[
            {"state": "Nhap", "action": "Phat lenh", "next_state": "Dang thu hoi", "allowed": "FS QA Manager"},
            {"state": "Dang thu hoi", "action": "Hoan tat", "next_state": "Cho phe duyet dong", "allowed": "FS QA Manager"},
            {"state": "Cho phe duyet dong", "action": "Phe duyet", "next_state": "Da dong", "allowed": "FS QA Manager"},
        ])

    _make("Doc Change Request Workflow", "Doc Change Request",
        states=[
            {"state": "Nhap", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Cho duyet", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Da duyet", "doc_status": "1", "allow_edit": "FS QA Manager"},
            {"state": "Tu choi", "doc_status": "0", "allow_edit": "FS QA Manager"},
        ],
        transitions=[
            {"state": "Nhap", "action": "Gui duyet", "next_state": "Cho duyet", "allowed": "FS QA Manager"},
            {"state": "Cho duyet", "action": "Phe duyet", "next_state": "Da duyet", "allowed": "FS QA Manager"},
            {"state": "Cho duyet", "action": "Tu choi", "next_state": "Tu choi", "allowed": "FS QA Manager"},
        ])

    _make("Label Approval Workflow", "Label Approval",
        states=[
            {"state": "Nhap", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Cho duyet", "doc_status": "0", "allow_edit": "FS QA Manager"},
            {"state": "Da duyet", "doc_status": "1", "allow_edit": "FS QA Manager"},
        ],
        transitions=[
            {"state": "Nhap", "action": "Gui duyet", "next_state": "Cho duyet", "allowed": "FS QA Manager"},
            {"state": "Cho duyet", "action": "Phe duyet", "next_state": "Da duyet", "allowed": "FS QA Manager"},
        ])
