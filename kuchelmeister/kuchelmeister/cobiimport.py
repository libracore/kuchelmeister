# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json      # to parse str to dict

@frappe.whitelist()
def import_customer(content):
    content = json.loads(content)
    
    new_customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": content['customer']['customer_name'],
        "customer_group": content['customer']['customer_group'],
        "customer_type": content['customer']['customer_type'],
        "territory": content['customer']['territory'],
        "tax_id": (content['customer']['tax_id'] or "?"),
        "branche": content['customer']['branche'],
        "grobeinteilung": content['customer']['grobeinteilung'],
        "klassifizierung": content['customer']['klassifizierung'],
        "language": content['customer']['language'],
        "website": content['customer']['website']
    })
    new_customer.insert()
    
    for address in content['addresses']:
        new_address = frappe.get_doc({
            "doctype": "Address",
            "address_title": address['address_title'],
            "address_type": address['address_type'],
            "address_line1": address['address_line1'],
            "address_line2": address['address_line2'],
            "pincode": address['pincode'],
            "plz": address['pincode'],
            "city": address['city'],
            "state": address['state'],
            "email_id": address['email_id'],
            "phone": address['phone'],
            "is_primary_address": address['is_primary_address'],
            "is_shipping_address": address['is_shipping_address']
        })
        new_address.append("links", {
            "link_doctype": "Customer",
            "link_name": new_customer.name
        })
        new_address.insert()
    
    for contact in content['contacts']:
        new_contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": contact['first_name'],
            "last_name": contact['last_name'],
            "bezeichnung": contact['bezeichnung'],
            "briefanrede": contact['briefanrede'],
            "designation": contact['designation'],
            "email_id": contact['email_id'],
            "interner_status": contact['interner_status'],
            "is_primary_contact": contact['is_primary_contact'],
            "mobile_no": contact['mobile_no'],
            "phone": contact['phone'],
            "salutation": contact['salutation']
        })
        new_contact.append("links", {
            "link_doctype": "Customer",
            "link_name": new_customer.name
        })
        if (contact['email_id']):
            new_contact.append("email_ids", {
                "email_id": contact['email_id'],
                "is_primary": 1
            })
        if contact['phone']:
            new_contact.append("phone_nos", {
                "phone": contact['phone'],
                "is_primary_phone": 1
            })
        if contact['mobile_no']:
            new_contact.append("phone_nos", {
                "phone": contact['mobile_no'],
                "is_primary_mobile_no": 1
            })
        new_contact.insert()
        
    frappe.db.commit()
    return new_customer.name
