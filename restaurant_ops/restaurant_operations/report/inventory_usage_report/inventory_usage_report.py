import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	conditions, values = [], {}
	if filters.get("from_date"):
		conditions.append("p.posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("p.posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("branch"):
		conditions.append("p.branch = %(branch)s")
		values["branch"] = filters["branch"]

	conditions.append("ifnull(sed.s_warehouse, '') != ''")
	conditions.append("ifnull(sed.t_warehouse, '') = ''")
	where = "where " + " and ".join(conditions)
	rows = frappe.db.sql(
		f"""
		select p.posting_date, p.branch, se.name stock_entry, sed.item_code,
			sed.item_name, abs(sed.qty) qty_used, sed.s_warehouse source_warehouse
		from `tabDaily Kitchen Production` p
		join `tabStock Entry` se on se.daily_kitchen_production = p.name
		join `tabStock Entry Detail` sed on sed.parent = se.name
		{where}
		order by p.posting_date desc, p.branch, sed.item_code
		""",
		values,
		as_dict=True,
	)
	return columns(), rows


def columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 170},
		{"label": _("Stock Entry"), "fieldname": "stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 180},
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("Qty Used"), "fieldname": "qty_used", "fieldtype": "Float", "width": 110},
		{"label": _("Source Warehouse"), "fieldname": "source_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 190},
	]
