// Copyright (c) 2016-2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Planning"] = {
	"filters": [
        {
			"fieldname":"only_reorder",
			"label": __("Only reorder"),
			"fieldtype": "Check",
			"default": 1
		}
	]
};
