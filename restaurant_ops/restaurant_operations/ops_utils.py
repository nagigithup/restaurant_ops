
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


@frappe.whitelist()
def get_item_defaults(item_code, purpose=None):
	if not item_code:
		return {}

	item = frappe.db.get_value("Item", item_code, ["item_name", "stock_uom"], as_dict=True) or {}
	return {
		"item_name": item.get("item_name"),
		"stock_uom": item.get("stock_uom"),
		"default_bom": _get_default_bom(item_code),
		"sales_rate": _get_item_rate(item_code, selling=True),
		"purchase_rate": _get_item_rate(item_code, buying=True),
	}


def _get_default_bom(item_code):
	filters = {"item": item_code, "docstatus": 1}
	if frappe.db.has_column("BOM", "is_active"):
		filters["is_active"] = 1

	order_by = "modified desc"
	if frappe.db.has_column("BOM", "is_default"):
		order_by = "is_default desc, modified desc"

	bom = frappe.db.get_all("BOM", filters=filters, fields=["name"], order_by=order_by, limit=1)
	return bom[0].name if bom else None


def _get_item_rate(item_code, selling=False, buying=False):
	if not frappe.db.exists("DocType", "Item Price"):
		return 0

	settings = get_settings()
	values = {"item_code": item_code}
	conditions = ["item_code = %(item_code)s"]

	if selling and frappe.db.has_column("Item Price", "selling"):
		conditions.append("selling = 1")
	if buying and frappe.db.has_column("Item Price", "buying"):
		conditions.append("buying = 1")
	if settings.default_price_list:
		conditions.append("price_list = %(price_list)s")
		values["price_list"] = settings.default_price_list

	rows = _get_item_price_rows(conditions, values)
	if not rows and "price_list = %(price_list)s" in conditions:
		conditions.remove("price_list = %(price_list)s")
		values.pop("price_list", None)
		rows = _get_item_price_rows(conditions, values)

	return flt(rows[0].price_list_rate) if rows else 0


def _get_item_price_rows(conditions, values):
	return frappe.db.sql(
		f"""
		select price_list_rate
		from `tabItem Price`
		where {" and ".join(conditions)}
		order by valid_from desc, modified desc
		limit 1
		""",
		values,
		as_dict=True,
	)
