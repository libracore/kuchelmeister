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
        },
        {
            "fieldname":"has_safety_stock",
            "label": __("Has safety stock"),
            "fieldtype": "Check",
            "default": 0
        },
        {
            "fieldname":"hide_no_transactions",
            "label": __("Hide no transactions"),
            "fieldtype": "Check",
            "default": 1
        },
        {
            "fieldname":"item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        }
    ]
};
