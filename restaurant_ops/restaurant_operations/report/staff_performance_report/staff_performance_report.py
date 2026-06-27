import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	rows = []
	for doctype, date_field, branch_field, amount_field in (
		("Daily Kitchen Production", "posting_date", "branch", None),
		("Daily Sales Summary", "posting_date", "branch", "total_amount"),
		("Daily Purchases", "posting_date", "branch", "total_amount"),
		("Kitchen Wastage", "posting_date", "branch", None),
	):
		rows.extend(_activity_rows(doctype, date_field, branch_field, amount_field, filters))
	return columns(), rows


def _activity_rows(doctype, date_field, branch_field, amount_field, filters):
	conditions, values = [], {}
	if filters.get("from_date"):
		conditions.append(f"{date_field} >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append(f"{date_field} <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("branch"):
		conditions.append(f"{branch_field} = %(branch)s")
		values["branch"] = filters["branch"]

	amount_select = f"sum({amount_field}) total_amount" if amount_field else "0 total_amount"
	where = "where " + " and ".join(conditions) if conditions else ""
	return frappe.db.sql(
		f"""
		select owner staff_user, '{doctype}' activity, {branch_field} branch,
			count(name) records, {amount_select}
		from `tab{doctype}`
		{where}
		group by owner, {branch_field}
		order by owner, activity
		""",
		values,
		as_dict=True,
	)


def columns():
	return [
		{"label": _("Staff User"), "fieldname": "staff_user", "fieldtype": "Link", "options": "User", "width": 190},
		{"label": _("Activity"), "fieldname": "activity", "fieldtype": "Data", "width": 190},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 170},
		{"label": _("Records"), "fieldname": "records", "fieldtype": "Int", "width": 100},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 140},
	]
