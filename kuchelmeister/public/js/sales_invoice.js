frappe.ui.form.on('Sales Invoice', {
    on_submit(frm) {
        // send sales invoice to RunMyAccounts
        frappe.call({
            method: "kuchelmeister.utils.runmyaccounts.create_invoice",
            args: {
                "sales_invoice": frm.doc.name
            },
            callback: function(response) {
                frappe.msgprint("Rechnung " + frm.doc.name + " an RunMyAccounts übertragen.");
            }
        });
    }
});
