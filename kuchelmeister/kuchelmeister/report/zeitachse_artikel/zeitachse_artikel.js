// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Zeitachse Artikel"] = {
	"filters": [
        {
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
            "options": "Item"
		}
	]
};
