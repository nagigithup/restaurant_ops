
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}; conditions=[]; values={}
	if filters.get("from_date"): conditions.append("p.posting_date >= %(from_date)s"); values["from_date"] = filters["from_date"]
	if filters.get("to_date"): conditions.append("p.posting_date <= %(to_date)s"); values["to_date"] = filters["to_date"]
	if filters.get("branch"): conditions.append("p.branch = %(branch)s"); values["branch"] = filters["branch"]
	where = "where " + " and ".join(conditions) if conditions else ""
	rows = frappe.db.sql(f"""select p.posting_date, p.branch, p.supplier, i.item, i.qty, i.rate, i.amount
		from `tabDaily Purchases` p join `tabDaily Purchase Item` i on i.parent=p.name {where}
		order by p.posting_date desc, p.branch, p.supplier""", values, as_dict=True)
	return columns(), rows


def columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 160},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 170},
		{"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 170},
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
		{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 120},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 130},
	]
