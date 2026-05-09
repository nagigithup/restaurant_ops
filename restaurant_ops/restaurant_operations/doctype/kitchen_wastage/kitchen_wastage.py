import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from restaurant_ops.restaurant_operations.ops_utils import apply_branch_defaults, cancel_or_delete, get_settings, require_rows, set_if_empty


class KitchenWastage(Document):
	def validate(self):
		if not self.posting_date:
			self.posting_date = nowdate()
		defaults = apply_branch_defaults(self)
		set_if_empty(self, "source_warehouse", defaults.get("finished_goods_warehouse"))
		settings = get_settings()
		set_if_empty(self, "expense_account", settings.default_wastage_expense_account)

	def create_wastage_stock_entry(self):
		require_rows(self, "wastage_items", _("Wasted Meals"))
		if self.linked_stock_entry:
			frappe.throw(_("Wastage Stock Entry already exists: {0}").format(self.linked_stock_entry))
		settings = get_settings()
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.purpose = "Material Issue"
		se.company = self.company
		se.posting_date = self.posting_date
		se.set_posting_time = 1
		if se.meta.has_field("kitchen_wastage"):
			se.kitchen_wastage = self.name
		for row in self.wastage_items:
			if flt(row.qty_wasted) <= 0:
				frappe.throw(_("Qty Wasted must be greater than zero for {0}.").format(row.meal_item))
			args = {"item_code": row.meal_item, "qty": row.qty_wasted, "s_warehouse": self.source_warehouse}
			if self.expense_account:
				args["expense_account"] = self.expense_account
			se.append("items", args)
		se.insert(ignore_permissions=True)
		if settings.auto_submit_stock_entries:
			se.submit()
		self.db_set("linked_stock_entry", se.name)
		return se.name

	def cancel_stock_entry(self):
		cancel_or_delete("Stock Entry", self.linked_stock_entry)
		self.db_set("linked_stock_entry", None)


@frappe.whitelist()
def create_wastage_stock_entry(name):
	return frappe.get_doc("Kitchen Wastage", name).create_wastage_stock_entry()


@frappe.whitelist()
def cancel_stock_entry(name):
	frappe.get_doc("Kitchen Wastage", name).cancel_stock_entry()
	return True
