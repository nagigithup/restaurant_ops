
function set_today(frm) {
	if (!frm.doc.posting_date) frm.set_value('posting_date', frappe.datetime.get_today());
}

function apply_branch_defaults(frm) {
	if (!frm.doc.branch) return;
	frappe.db.get_doc('Restaurant Branch', frm.doc.branch).then(branch => {
		frm.set_value('company', branch.company || '');
		if (frm.doctype === 'Daily Kitchen Production') {
			(frm.doc.production_items || []).forEach(row => {
				frappe.model.set_value(row.doctype, row.name, 'raw_material_warehouse', row.raw_material_warehouse || branch.raw_material_warehouse);
				frappe.model.set_value(row.doctype, row.name, 'wip_warehouse', row.wip_warehouse || branch.wip_warehouse);
				frappe.model.set_value(row.doctype, row.name, 'finished_goods_warehouse', row.finished_goods_warehouse || branch.finished_goods_warehouse);
			});
		}
		if (frm.doctype === 'Daily Sales Summary') {
			if (!frm.doc.customer) frm.set_value('customer', branch.daily_sales_customer || '');
			if (!frm.doc.sales_warehouse) frm.set_value('sales_warehouse', branch.finished_goods_warehouse || '');
		}
		if (frm.doctype === 'Daily Purchases') {
			if (!frm.doc.supplier) frm.set_value('supplier', branch.default_supplier || '');
			if (!frm.doc.raw_material_warehouse) frm.set_value('raw_material_warehouse', branch.raw_material_warehouse || '');
		}
		if (frm.doctype === 'Kitchen Wastage') {
			if (!frm.doc.source_warehouse) frm.set_value('source_warehouse', branch.finished_goods_warehouse || '');
		}
	});
}

function call_action(frm, method) {
	frappe.call({method, args: {name: frm.doc.name}, freeze: true, callback: () => frm.reload_doc()});
}

function set_item_defaults(cdt, cdn) {
	let row = locals[cdt][cdn];
	if (!row || !row.meal_item) return;
	frappe.call({
		method: 'restaurant_ops.restaurant_operations.ops_utils.get_item_defaults',
		args: {item_code: row.meal_item, purpose: 'wastage'},
		callback(r) {
			let details = r.message || {};
			frappe.model.set_value(cdt, cdn, 'item_name', details.item_name || '');
		}
	});
}

frappe.ui.form.on('Kitchen Wastage', {
	onload: set_today,
	branch: apply_branch_defaults,
	refresh(frm) {
		apply_branch_defaults(frm);
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Wastage Stock Entry'), () => call_action(frm, 'restaurant_ops.restaurant_operations.doctype.kitchen_wastage.kitchen_wastage.create_wastage_stock_entry')).addClass('btn-primary');
			frm.add_custom_button(__('View Stock Entry'), () => frm.doc.linked_stock_entry && frappe.set_route('Form', 'Stock Entry', frm.doc.linked_stock_entry));
			frm.add_custom_button(__('Cancel Stock Entry'), () => call_action(frm, 'restaurant_ops.restaurant_operations.doctype.kitchen_wastage.kitchen_wastage.cancel_stock_entry'));
		}
	}
});

frappe.ui.form.on('Kitchen Wastage Item', {
	meal_item(frm, cdt, cdn) {
		set_item_defaults(cdt, cdn);
	}
});
