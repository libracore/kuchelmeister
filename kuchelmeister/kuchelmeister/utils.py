# Copyright (c) 2019-2022, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_blanket_order(quotation):
    blanket_order = get_mapped_doc("Quotation", quotation, 
        {
            "Quotation": {
                "doctype": "Blanket Order",
                "field_map": {
                    "request_no": "external_reference",
                    "party_name": "customer"
                }
            },
            "Quotation Item": {
                "doctype": "Blanket Order Item"
            }
        }
    )
    ## add values
    blanket_order.order_type = "Selling"
    # update status
    frappe.db.sql("""UPDATE `tabQuotation` SET `status` = "Ordered" WHERE `name` = "{0}";""".format(quotation))
    frappe.db.commit()
    return blanket_order
