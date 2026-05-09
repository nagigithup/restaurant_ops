
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

function sales_total(frm) {
	let total = 0;
	(frm.doc.sales_items || []).forEach(row => total += flt(row.qty_sold) * flt(row.rate));
	frm.set_value('total_amount', total);
}
frappe.ui.form.on('Daily Sales Summary', {
	onload: set_today,
	branch: apply_branch_defaults,
	refresh(frm) {
		apply_branch_defaults(frm); sales_total(frm);
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Sales Invoice'), () => call_action(frm, 'restaurant_ops.restaurant_operations.doctype.daily_sales_summary.daily_sales_summary.create_sales_invoice')).addClass('btn-primary');
			frm.add_custom_button(__('View Sales Invoice'), () => frm.doc.linked_sales_invoice && frappe.set_route('Form', 'Sales Invoice', frm.doc.linked_sales_invoice));
			frm.add_custom_button(__('Cancel Sales Invoice'), () => call_action(frm, 'restaurant_ops.restaurant_operations.doctype.daily_sales_summary.daily_sales_summary.cancel_sales_invoice'));
		}
	}
});
frappe.ui.form.on('Daily Sales Summary Item', { qty_sold(frm, cdt, cdn) { let r = locals[cdt][cdn]; frappe.model.set_value(cdt, cdn, 'amount', flt(r.qty_sold) * flt(r.rate)); sales_total(frm); }, rate(frm, cdt, cdn) { let r = locals[cdt][cdn]; frappe.model.set_value(cdt, cdn, 'amount', flt(r.qty_sold) * flt(r.rate)); sales_total(frm); } });
