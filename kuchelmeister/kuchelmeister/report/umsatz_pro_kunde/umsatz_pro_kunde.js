// Copyright (c) 2016-2019, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Umsatz pro Kunde"] = {
	"filters": [
        {
            "fieldname":"from_date",
            "label": __("From date"),
            "fieldtype": "Date",
            "default": new Date().getFullYear() + "-01-01"
        },
        {
            "fieldname":"end_date",
            "label": __("End date"),
            "fieldtype": "Date",
            "default" : frappe.datetime.get_today()
        }
	]
};
