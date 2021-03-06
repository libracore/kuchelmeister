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
        // address filters
        cur_frm.fields_dict.supplier_address.get_query = function(doc) {
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
    },
    supplier_address: function(frm) {
        if (frm.doc.supplier_address) {
            // get contact name
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "Address",
                    "name": frm.doc.supplier_address
                },
                "callback": function(response) {
                    var address = response.message;

                    if (address) {
                        var display = address.address_line1;
                        if (address.address_line2) { display += "<br>" + address.address_line2; }
                        display += "<br>" + address.pincode + " " + address.city;
                        display += "<br>" + address.country;
                        frm.set_value('address_display', display);
                    }
                }
            });
        }
    },
    sales_order: function(frm) {
        if (frm.doc.sales_order) { fetch_items_from_sales_order(frm); }
    }
});

function fetch_items_from_sales_order(frm) {
    if (frm.doc.sales_order) {
        frappe.call({
            'method': 'frappe.client.get',
            'args': {
                'doctype': 'Sales Order',
                'name': frm.doc.sales_order
            },
            'callback': function(response) {
                var sales_order = response.message;
                for (var i = 0; i < sales_order.items.length; i++) {
                    var child = cur_frm.add_child('items');
                    frappe.model.set_value(child.doctype, child.name, 'item', sales_order.items[i].item_code);
                    frappe.model.set_value(child.doctype, child.name, 'item_name', sales_order.items[i].item_name);
                    frappe.model.set_value(child.doctype, child.name, 'stock_uom', sales_order.items[i].stock_uom);
                    frappe.model.set_value(child.doctype, child.name, 'qty', sales_order.items[i].qty);
                    cur_frm.refresh_field('items');
                }
            }
        });
    }
}
