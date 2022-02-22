// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Kennzahlen"] = {
	"filters": [
		{
			fieldname:"from_date",
			label: __("From date"),
			fieldtype: "Date",
			default: new Date(new Date().getFullYear(), 0, 1),
			reqd: 1,
		},
        {
			fieldname:"to_date",
			label: __("To date"),
			fieldtype: "Date",
			default: new Date(),
			reqd: 1,
		}
	]
};
