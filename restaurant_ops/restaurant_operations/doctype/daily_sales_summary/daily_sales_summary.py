import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from restaurant_ops.restaurant_operations.ops_utils import apply_branch_defaults, cancel_or_delete, get_settings, require_rows, set_if_empty


class DailySalesSummary(Document):
	def validate(self):
		if not self.posting_date:
			self.posting_date = nowdate()
		defaults = apply_branch_defaults(self)
		set_if_empty(self, "customer", defaults.get("customer"))
		set_if_empty(self, "sales_warehouse", defaults.get("finished_goods_warehouse"))
		total = 0
		for row in self.sales_items:
			row.amount = flt(row.qty_sold) * flt(row.rate)
			total += row.amount
		self.total_amount = total

	def create_sales_invoice(self):
		require_rows(self, "sales_items", _("Meals Sold"))
		if self.linked_sales_invoice:
			frappe.throw(_("Sales Invoice already exists: {0}").format(self.linked_sales_invoice))
		settings = get_settings()
		si = frappe.new_doc("Sales Invoice")
		si.company = self.company
		si.customer = self.customer
		si.posting_date = self.posting_date
		si.set_posting_time = 1
		si.update_stock = 1
		si.set_warehouse = self.sales_warehouse
		if settings.default_price_list:
			si.selling_price_list = settings.default_price_list
		if settings.default_receivable_account:
			si.debit_to = settings.default_receivable_account
		if si.meta.has_field("daily_sales_summary"):
			si.daily_sales_summary = self.name
		for row in self.sales_items:
			if flt(row.qty_sold) <= 0:
				frappe.throw(_("Qty Sold must be greater than zero for {0}.").format(row.meal_item))
			item = {"item_code": row.meal_item, "qty": row.qty_sold, "rate": row.rate, "warehouse": self.sales_warehouse}
			if settings.default_income_account:
				item["income_account"] = settings.default_income_account
			si.append("items", item)
		si.insert(ignore_permissions=True)
		if settings.auto_submit_sales_invoice:
			si.submit()
		self.db_set("linked_sales_invoice", si.name)
		return si.name

	def cancel_sales_invoice(self):
		cancel_or_delete("Sales Invoice", self.linked_sales_invoice)
		self.db_set("linked_sales_invoice", None)


@frappe.whitelist()
def create_sales_invoice(name):
	doc = frappe.get_doc("Daily Sales Summary", name)
	return doc.create_sales_invoice()


@frappe.whitelist()
def cancel_sales_invoice(name):
	doc = frappe.get_doc("Daily Sales Summary", name)
	doc.cancel_sales_invoice()
	return True
