import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from restaurant_ops.restaurant_operations.ops_utils import apply_branch_defaults, cancel_or_delete, get_settings, require_rows, set_if_empty


class DailyPurchases(Document):
	def validate(self):
		if not self.posting_date:
			self.posting_date = nowdate()
		defaults = apply_branch_defaults(self)
		set_if_empty(self, "supplier", defaults.get("supplier"))
		set_if_empty(self, "raw_material_warehouse", defaults.get("raw_material_warehouse"))
		total = 0
		for row in self.purchase_items:
			row.amount = flt(row.qty) * flt(row.rate)
			total += row.amount
		self.total_amount = total

	def _purchase_item_args(self, row):
		args = {"item_code": row.item, "qty": row.qty, "rate": row.rate, "warehouse": self.raw_material_warehouse}
		if row.uom:
			args["uom"] = row.uom
		return args

	def create_purchase_invoice(self):
		require_rows(self, "purchase_items", _("Purchased Raw Materials"))
		if self.linked_purchase_invoice:
			frappe.throw(_("Purchase Invoice already exists: {0}").format(self.linked_purchase_invoice))
		settings = get_settings()
		pi = frappe.new_doc("Purchase Invoice")
		pi.company = self.company
		pi.supplier = self.supplier
		pi.posting_date = self.posting_date
		pi.set_posting_time = 1
		pi.update_stock = 1
		pi.set_warehouse = self.raw_material_warehouse
		if settings.default_payable_account:
			pi.credit_to = settings.default_payable_account
		if pi.meta.has_field("daily_purchases"):
			pi.daily_purchases = self.name
		for row in self.purchase_items:
			if flt(row.qty) <= 0:
				frappe.throw(_("Purchase quantity must be greater than zero for {0}.").format(row.item))
			pi.append("items", self._purchase_item_args(row))
		pi.insert(ignore_permissions=True)
		if settings.auto_submit_purchase_invoice:
			pi.submit()
		self.db_set("linked_purchase_invoice", pi.name)
		return pi.name

	def create_purchase_receipt(self):
		require_rows(self, "purchase_items", _("Purchased Raw Materials"))
		if self.linked_purchase_receipt:
			frappe.throw(_("Purchase Receipt already exists: {0}").format(self.linked_purchase_receipt))
		settings = get_settings()
		pr = frappe.new_doc("Purchase Receipt")
		pr.company = self.company
		pr.supplier = self.supplier
		pr.posting_date = self.posting_date
		pr.set_posting_time = 1
		pr.set_warehouse = self.raw_material_warehouse
		if pr.meta.has_field("daily_purchases"):
			pr.daily_purchases = self.name
		for row in self.purchase_items:
			if flt(row.qty) <= 0:
				frappe.throw(_("Purchase quantity must be greater than zero for {0}.").format(row.item))
			pr.append("items", self._purchase_item_args(row))
		pr.insert(ignore_permissions=True)
		if settings.auto_submit_purchase_receipt:
			pr.submit()
		self.db_set("linked_purchase_receipt", pr.name)
		return pr.name

	def cancel_purchase_documents(self):
		cancel_or_delete("Purchase Invoice", self.linked_purchase_invoice)
		cancel_or_delete("Purchase Receipt", self.linked_purchase_receipt)
		self.db_set("linked_purchase_invoice", None)
		self.db_set("linked_purchase_receipt", None)


@frappe.whitelist()
def create_purchase_invoice(name):
	return frappe.get_doc("Daily Purchases", name).create_purchase_invoice()


@frappe.whitelist()
def create_purchase_receipt(name):
	return frappe.get_doc("Daily Purchases", name).create_purchase_receipt()


@frappe.whitelist()
def cancel_purchase_documents(name):
	frappe.get_doc("Daily Purchases", name).cancel_purchase_documents()
	return True
