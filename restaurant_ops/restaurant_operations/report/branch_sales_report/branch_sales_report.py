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
		select posting_date, branch, customer, count(name) summaries, sum(total_amount) total_sales
		from `tabDaily Sales Summary`
		{where}
		group by posting_date, branch, customer
		order by posting_date desc, branch
		""",
		values,
		as_dict=True,
	)
	return columns(), rows


def columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 180},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": _("Sales Summaries"), "fieldname": "summaries", "fieldtype": "Int", "width": 130},
		{"label": _("Total Sales"), "fieldname": "total_sales", "fieldtype": "Currency", "width": 140},
	]
