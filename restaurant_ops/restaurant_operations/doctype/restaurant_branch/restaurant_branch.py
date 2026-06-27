from frappe.model.naming import make_autoname
from frappe.model.document import Document


class RestaurantBranch(Document):
	def autoname(self):
		self.name = make_autoname("HB.####")
