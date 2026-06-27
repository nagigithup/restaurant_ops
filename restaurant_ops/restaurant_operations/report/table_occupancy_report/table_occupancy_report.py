import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	conditions, values = [], {}
	if filters.get("from_date"):
		conditions.append("posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
		values["branch"] = filters["branch"]

	where = "where " + " and ".join(conditions) if conditions else ""
	rows = frappe.db.sql(
		f"""
		select posting_date, branch, name sales_summary, '' restaurant_table,
			0 covers, total_amount
		from `tabDaily Sales Summary`
		{where}
		order by posting_date desc, branch
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
		{"label": _("Table"), "fieldname": "restaurant_table", "fieldtype": "Data", "width": 120},
		{"label": _("Covers"), "fieldname": "covers", "fieldtype": "Int", "width": 100},
		{"label": _("Sales Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 140},
	]
