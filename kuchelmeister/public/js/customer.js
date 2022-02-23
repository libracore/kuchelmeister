/* add Kundenbesuch to customer dashboard, only works for v11 and above */
try {
    cur_frm.dashboard.add_transactions([
        {
            'label': __('Other'),
            'items': ['Kundenbesuch']
        }
    ]);
} catch { /* do nothing for older versions */ }


frappe.ui.form.on('Customer', {
    after_insert(frm) {
        // send customer to RunMyAccounts
        frappe.call({
            method: "kuchelmeister.utils.runmyaccounts.create_customer",
            args: {
                "customer": frm.doc.name
            },
            callback: function(response) {
                frappe.msgprint("RunMyAccounts aktualisiert");
            }
        });
    }
});
