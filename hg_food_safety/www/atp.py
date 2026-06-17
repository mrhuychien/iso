"""Context cho portal SPA ATTP. Yeu cau dang nhap; bom context cho client."""
import frappe
from frappe.utils import now


def _get_csrf():
    """Lay CSRF token an toan qua nhieu phien ban Frappe."""
    try:
        return frappe.sessions.get_csrf_token()
    except Exception:
        try:
            return frappe.local.session.data.csrf_token or ""
        except Exception:
            return ""


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/atp"
        raise frappe.Redirect

    roles = set(frappe.get_roles())
    context.no_cache = 1
    context.fs_user = frappe.session.user
    context.fs_is_manager = 1 if ({"FS QA Manager", "System Manager"} & roles) else 0
    context.fs_asset_version = now().replace(" ", "T").replace(":", "-").replace(".", "-")
    context.fs_csrf = _get_csrf()
    return context
