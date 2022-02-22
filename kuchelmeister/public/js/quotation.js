frappe.ui.form.on('Quotation', {
    refresh(frm) {
        if (frm.doc.status === "Open") {
            frm.add_custom_button(__("Blanket Order"), function() {
                create_blanket_order(frm);
            }, __("Create") );
        }
    }
});

function create_blanket_order(frm) {
    frappe.model.open_mapped_doc({
        'method': 'kuchelmeister.kuchelmeister.utils.create_blanket_order',
        'frm': frm
    });
}
