import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	conditions, values = [], {}
	if filters.get("from_date"):
		conditions.append("s.posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("s.posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("branch"):
		conditions.append("s.branch = %(branch)s")
		values["branch"] = filters["branch"]

	where = "where " + " and ".join(conditions) if conditions else ""
	rows = frappe.db.sql(
		f"""
		select s.posting_date, s.branch, s.name sales_summary, i.meal_item, i.item_name,
			i.qty_sold, i.rate, i.amount
		from `tabDaily Sales Summary` s
		join `tabDaily Sales Summary Item` i on i.parent = s.name
		{where}
		order by s.posting_date desc, s.branch, s.name
		""",
		values,
		as_dict=True,
	)
	return columns(), rows


def columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 170},
		{"label": _("Sales Summary"), "fieldname": "sales_summary", "fieldtype": "Link", "options": "Daily Sales Summary", "width": 180},
		{"label": _("Item Code"), "fieldname": "meal_item", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("Qty Sold"), "fieldname": "qty_sold", "fieldtype": "Float", "width": 100},
		{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 110},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 130},
	]
