
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

function set_item_defaults(cdt, cdn, item_field, purpose) {
	let row = locals[cdt][cdn];
	if (!row || !row[item_field]) return;
	frappe.call({
		method: 'restaurant_ops.restaurant_operations.ops_utils.get_item_defaults',
		args: {item_code: row[item_field], purpose},
		callback(r) {
			let details = r.message || {};
			frappe.model.set_value(cdt, cdn, 'item_name', details.item_name || '');
			if (purpose === 'production' && details.default_bom) {
				frappe.model.set_value(cdt, cdn, 'bom', details.default_bom);
			}
		}
	});
}

frappe.ui.form.on('Daily Kitchen Production', {
	onload: set_today,
	branch: apply_branch_defaults,
	refresh(frm) {
		apply_branch_defaults(frm);
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Manufacture Stock Entries'), () => call_action(frm, 'restaurant_ops.restaurant_operations.doctype.daily_kitchen_production.daily_kitchen_production.create_manufacture_stock_entries')).addClass('btn-primary');
			frm.add_custom_button(__('View Stock Entries'), () => frappe.set_route('List', 'Stock Entry', {daily_kitchen_production: frm.doc.name}));
			frm.add_custom_button(__('Cancel Linked Stock Entries'), () => call_action(frm, 'restaurant_ops.restaurant_operations.doctype.daily_kitchen_production.daily_kitchen_production.cancel_linked_stock_entries'));
		}
	}
});

frappe.ui.form.on('Daily Kitchen Production Item', {
	meal_item(frm, cdt, cdn) {
		set_item_defaults(cdt, cdn, 'meal_item', 'production');
	}
});
