// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Anmeldung Subakkordant', {
	refresh: function(frm) {
        // contact filters
        cur_frm.fields_dict.contact.get_query = function(doc) {
             return {
                 filters: {
                     "link_doctype": "Supplier",
                     "link_name": frm.doc.supplier
                 }
             };
        };
        // set default date
        if (!frm.doc.date) {
            cur_frm.set_value("date", new Date());
        }
	},
    contact: function(frm) {
        if (frm.doc.contact) {
            // get contact name
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "Contact",
                    "name": frm.doc.contact
                },
                "callback": function(response) {
                    var contact = response.message;

                    if (contact) {
                        frm.set_value('contact_name', (contact.first_name || "") + " " + (contact.last_name || ""));
                    }
                }
            });
        }
    }
});
