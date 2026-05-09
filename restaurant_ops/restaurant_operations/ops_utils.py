
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate


def get_settings():
	return frappe.get_single("Restaurant Settings")


def get_branch_defaults(branch):
	if not branch:
		return {}
	doc = frappe.get_doc("Restaurant Branch", branch)
	return {
		"company": doc.company,
		"raw_material_warehouse": doc.raw_material_warehouse,
		"wip_warehouse": doc.wip_warehouse,
		"finished_goods_warehouse": doc.finished_goods_warehouse,
		"cost_center": doc.cost_center,
		"customer": doc.daily_sales_customer,
		"supplier": doc.default_supplier,
	}


def ensure_posting_date(doc):
	if not doc.posting_date:
		doc.posting_date = nowdate()


def set_if_empty(doc, fieldname, value):
	if value and not doc.get(fieldname):
		doc.set(fieldname, value)


def require_rows(doc, table_field, label):
	if not doc.get(table_field):
		frappe.throw(_("Add at least one row in {0} before creating documents.").format(label))


def submit_if(doc, enabled):
	doc.insert(ignore_permissions=True)
	if enabled:
		doc.submit()
	return doc


def cancel_or_delete(doctype, name):
	if not name or not frappe.db.exists(doctype, name):
		return
	doc = frappe.get_doc(doctype, name)
	if doc.docstatus == 1:
		doc.cancel()
	elif doc.docstatus == 0:
		frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)


def apply_branch_defaults(doc):
	defaults = get_branch_defaults(doc.branch)
	set_if_empty(doc, "company", defaults.get("company"))
	return defaults
