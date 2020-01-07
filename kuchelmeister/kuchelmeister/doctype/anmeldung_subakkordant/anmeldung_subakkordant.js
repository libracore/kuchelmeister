// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Anmeldung Subakkordant', {
	refresh: function(frm) {

	},
    contact: function(frm) {
        if (frm.doc.contact) {
            // contact filters
            cur_frm.fields_dict.contact.get_query = function(doc) {
                 return {
                     filters: {
                         "link_doctype": "Supplier",
                         "link_name": frm.doc.supplier
                     }
                 };
            };
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
