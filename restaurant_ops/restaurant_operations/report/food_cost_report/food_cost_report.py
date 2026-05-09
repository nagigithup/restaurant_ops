
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	rows = frappe.db.sql("""
		select b.item as meal_item, b.name as bom, b.total_cost as bom_cost,
			coalesce(ip.price_list_rate, 0) as selling_rate
		from `tabBOM` b
		left join `tabItem Price` ip on ip.item_code=b.item and ip.selling=1
		where b.is_active=1 and b.is_default=1
		order by b.item
	""", as_dict=True)
	seen = set(); data = []
	for row in rows:
		if row.meal_item in seen: continue
		seen.add(row.meal_item)
		row.gross_margin = flt(row.selling_rate) - flt(row.bom_cost)
		row.gross_margin_pct = (row.gross_margin / flt(row.selling_rate) * 100) if flt(row.selling_rate) else 0
		data.append(row)
	return columns(), data


def columns():
	return [
		{"label": _("Meal Item"), "fieldname": "meal_item", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": _("BOM"), "fieldname": "bom", "fieldtype": "Link", "options": "BOM", "width": 160},
		{"label": _("BOM Cost"), "fieldname": "bom_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Selling Rate"), "fieldname": "selling_rate", "fieldtype": "Currency", "width": 130},
		{"label": _("Gross Margin"), "fieldname": "gross_margin", "fieldtype": "Currency", "width": 130},
		{"label": _("Gross Margin %"), "fieldname": "gross_margin_pct", "fieldtype": "Percent", "width": 130},
	]
