import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from restaurant_ops.restaurant_operations.ops_utils import apply_branch_defaults, cancel_or_delete, get_settings, require_rows


class DailyKitchenProduction(Document):
	def validate(self):
		if not self.posting_date:
			self.posting_date = nowdate()
		defaults = apply_branch_defaults(self)
		for row in self.production_items:
			row.raw_material_warehouse = row.raw_material_warehouse or defaults.get("raw_material_warehouse")
			row.wip_warehouse = row.wip_warehouse or defaults.get("wip_warehouse")
			row.finished_goods_warehouse = row.finished_goods_warehouse or defaults.get("finished_goods_warehouse")

	def create_manufacture_stock_entries(self):
		require_rows(self, "production_items", _("Meals Produced"))
		if self.linked_stock_entries:
			frappe.throw(_("Stock Entries already exist for this production. Use View Stock Entries or cancel them first."))
		settings = get_settings()
		for row in self.production_items:
			if not row.bom:
				frappe.throw(_("Recipe / BOM is required for row {0}.").format(row.idx))
			if not row.raw_material_warehouse or not row.finished_goods_warehouse:
				frappe.throw(_("Raw Materials and Finished Meals warehouses are required for {0}.").format(row.meal_item))
			if flt(row.qty_produced) <= 0:
				frappe.throw(_("Qty Produced must be greater than zero for {0}.").format(row.meal_item))
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Manufacture"
			se.purpose = "Manufacture"
			se.company = self.company
			se.posting_date = self.posting_date
			se.set_posting_time = 1
			se.bom_no = row.bom
			se.from_bom = 1
			se.fg_completed_qty = flt(row.qty_produced)
			se.from_warehouse = row.raw_material_warehouse
			se.to_warehouse = row.finished_goods_warehouse
			if row.wip_warehouse:
				se.wip_warehouse = row.wip_warehouse
			if se.meta.has_field("daily_kitchen_production"):
				se.daily_kitchen_production = self.name
			se.get_items()
			se.insert(ignore_permissions=True)
			if settings.auto_submit_stock_entries:
				se.submit()
			self.append("linked_stock_entries", {"stock_entry": se.name, "meal_item": row.meal_item, "qty": row.qty_produced})
		self.status = "Completed" if settings.auto_submit_stock_entries else "Stock Entry Created"
		self.save(ignore_permissions=True)
		return [row.stock_entry for row in self.linked_stock_entries]

	def cancel_linked_stock_entries(self):
		for row in list(self.linked_stock_entries):
			cancel_or_delete("Stock Entry", row.stock_entry)
		self.set("linked_stock_entries", [])
		self.status = "Draft"
		self.save(ignore_permissions=True)


@frappe.whitelist()
def create_manufacture_stock_entries(name):
	doc = frappe.get_doc("Daily Kitchen Production", name)
	return doc.create_manufacture_stock_entries()


@frappe.whitelist()
def cancel_linked_stock_entries(name):
	doc = frappe.get_doc("Daily Kitchen Production", name)
	doc.cancel_linked_stock_entries()
	return True
