// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.listview_settings['Customer'] = {
    onload: function(listview) {
        listview.page.add_menu_item(__("CobiImport"), function() {
            frappe.prompt([
                {'fieldname': 'code', 'fieldtype': 'Code', 'label': 'Code', 'reqd': 1}  
            ],
            function(values){
                frappe.call({
                    "method": "kuchelmeister.kuchelmeister.cobiimport.import_customer",
                    "args": {
                        "content": values.code
                    },
                    "callback": function(response) {
                        frappe.set_route("Form", "Customer", response.message);
                    }
                });
            },
            __('CobiImport'),
            __('OK')
            )
        });
    }
};
