
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	conditions = []
	values = {}
	if filters.get("from_date"):
		conditions.append("x.posting_date >= %(from_date)s"); values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("x.posting_date <= %(to_date)s"); values["to_date"] = filters["to_date"]
	if filters.get("branch"):
		conditions.append("x.branch = %(branch)s"); values["branch"] = filters["branch"]
	where = "where " + " and ".join(conditions) if conditions else ""
	rows = frappe.db.sql(f"""
		select x.posting_date, x.branch, x.meal_item,
			sum(x.produced_qty) produced_qty, sum(x.sold_qty) sold_qty, sum(x.wasted_qty) wasted_qty
		from (
			select p.posting_date, p.branch, i.meal_item, i.qty_produced produced_qty, 0 sold_qty, 0 wasted_qty
			from `tabDaily Kitchen Production` p join `tabDaily Kitchen Production Item` i on i.parent=p.name
			union all
			select s.posting_date, s.branch, i.meal_item, 0, i.qty_sold, 0
			from `tabDaily Sales Summary` s join `tabDaily Sales Summary Item` i on i.parent=s.name
			union all
			select w.posting_date, w.branch, i.meal_item, 0, 0, i.qty_wasted
			from `tabKitchen Wastage` w join `tabKitchen Wastage Item` i on i.parent=w.name
		) x {where}
		group by x.posting_date, x.branch, x.meal_item order by x.posting_date desc, x.branch, x.meal_item
	""", values, as_dict=True)
	for row in rows:
		row.remaining_qty = flt(row.produced_qty) - flt(row.sold_qty) - flt(row.wasted_qty)
	return columns(), rows


def columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Restaurant Branch", "width": 160},
		{"label": _("Meal Item"), "fieldname": "meal_item", "fieldtype": "Link", "options": "Item", "width": 170},
		{"label": _("Produced Qty"), "fieldname": "produced_qty", "fieldtype": "Float", "width": 120},
		{"label": _("Sold Qty"), "fieldname": "sold_qty", "fieldtype": "Float", "width": 110},
		{"label": _("Wasted Qty"), "fieldname": "wasted_qty", "fieldtype": "Float", "width": 110},
		{"label": _("Remaining Qty"), "fieldname": "remaining_qty", "fieldtype": "Float", "width": 130},
	]
