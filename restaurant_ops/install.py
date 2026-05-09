import frappe

ROLES = ("Restaurant Manager", "Kitchen User", "Cashier User", "Purchase User", "Restaurant Accountant")
CUSTOM_FIELDS = {
	"Stock Entry": [
		{"fieldname": "daily_kitchen_production", "fieldtype": "Link", "label": "Daily Kitchen Production", "options": "Daily Kitchen Production", "insert_after": "stock_entry_type"},
		{"fieldname": "kitchen_wastage", "fieldtype": "Link", "label": "Kitchen Wastage", "options": "Kitchen Wastage", "insert_after": "daily_kitchen_production"},
	],
	"Sales Invoice": [
		{"fieldname": "daily_sales_summary", "fieldtype": "Link", "label": "Daily Sales Summary", "options": "Daily Sales Summary", "insert_after": "customer"},
	],
	"Purchase Invoice": [
		{"fieldname": "daily_purchases", "fieldtype": "Link", "label": "Daily Purchases", "options": "Daily Purchases", "insert_after": "supplier"},
	],
	"Purchase Receipt": [
		{"fieldname": "daily_purchases", "fieldtype": "Link", "label": "Daily Purchases", "options": "Daily Purchases", "insert_after": "supplier"},
	],
}


def after_install():
	_setup()


def after_migrate():
	_setup()


def _setup():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)
	for dt, fields in CUSTOM_FIELDS.items():
		if not frappe.db.exists("DocType", dt):
			continue
		for field in fields:
			name = f"{dt}-{field['fieldname']}"
			if not frappe.db.exists("Custom Field", name):
				frappe.get_doc({"doctype": "Custom Field", "dt": dt, "in_standard_filter": 1, **field}).insert(ignore_permissions=True)
	frappe.db.commit()
