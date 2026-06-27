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
		select i.meal_item, max(i.item_name) item_name, s.branch,
			sum(i.qty_sold) qty_sold, sum(i.amount) sales_amount, avg(i.rate) average_rate
		from `tabDaily Sales Summary` s
		join `tabDaily Sales Summary Item` i on i.parent = s.name
		{where}
		group by i.meal_item, s.branch
		order by sales_amount desc, qty_sold desc
		""",
		values,
		as_dict=True,
	)
	return columns(), rows


def columns():
	return [
		{"label": _("Item Code"), "fieldname": "meal_item", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 190},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 170},
		{"label": _("Qty Sold"), "fieldname": "qty_sold", "fieldtype": "Float", "width": 110},
		{"label": _("Sales Amount"), "fieldname": "sales_amount", "fieldtype": "Currency", "width": 140},
		{"label": _("Average Rate"), "fieldname": "average_rate", "fieldtype": "Currency", "width": 130},
	]
