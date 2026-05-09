
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}; conditions=[]; values={}
	if filters.get("from_date"): conditions.append("w.posting_date >= %(from_date)s"); values["from_date"] = filters["from_date"]
	if filters.get("to_date"): conditions.append("w.posting_date <= %(to_date)s"); values["to_date"] = filters["to_date"]
	if filters.get("branch"): conditions.append("w.branch = %(branch)s"); values["branch"] = filters["branch"]
	where = "where " + " and ".join(conditions) if conditions else ""
	rows = frappe.db.sql(f"""select w.posting_date, w.branch, i.meal_item, i.qty_wasted, i.reason,
		coalesce(b.total_cost, 0) * i.qty_wasted as estimated_cost
		from `tabKitchen Wastage` w join `tabKitchen Wastage Item` i on i.parent=w.name
		left join `tabBOM` b on b.item=i.meal_item and b.is_default=1 and b.is_active=1
		{where} order by w.posting_date desc, w.branch, i.meal_item""", values, as_dict=True)
	return columns(), rows


def columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 160},
		{"label": _("Meal Item"), "fieldname": "meal_item", "fieldtype": "Link", "options": "Item", "width": 170},
		{"label": _("Qty Wasted"), "fieldname": "qty_wasted", "fieldtype": "Float", "width": 120},
		{"label": _("Reason"), "fieldname": "reason", "fieldtype": "Data", "width": 120},
		{"label": _("Estimated Cost"), "fieldname": "estimated_cost", "fieldtype": "Currency", "width": 140},
	]
