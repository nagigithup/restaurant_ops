frappe.query_reports['Staff Performance Report'] = {
	filters: [
		{fieldname: 'from_date', label: __('From Date'), fieldtype: 'Date'},
		{fieldname: 'to_date', label: __('To Date'), fieldtype: 'Date'},
		{fieldname: 'branch', label: __('Branch'), fieldtype: 'Link', options: 'Restaurant Branch'}
	]
};
