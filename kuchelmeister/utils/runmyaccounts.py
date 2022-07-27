# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
import frappe
from frappe import _
import urllib.request
import requests
import json
from datetime import datetime, timedelta
from frappe.utils import cint

TEST_HOST = "https://service.int.runmyaccounts.com"
LIVE_HOST = "https://service.runmyaccounts.com"

# create customer
@frappe.whitelist()
def create_customer(customer, debug=False):
    if cint(frappe.get_value("RunMyAccounts Settings", "RunMyAccounts Settings", "enabled")) == 0:
        print("RunMyAccounts is disabled")
        return
    
    if type(customer) == str:
        customer_doc = frappe.get_doc("Customer", customer)
    else:
        customer_doc = customer
    
    # prepare data structure (see https://www.runmyaccounts.ch/support-artikel/customer-entity/)
    data = {
        "customernumber": customer_doc.name,
        "name": customer_doc.customer_name[:64],
        #"created": customer_doc.creation.strftime("%Y-%m-%dT%H:%M:%S"), # not used, since on update this comes as a str from the form
        # "language_code": customer_doc.language,        # not used: yields "Die Sprache 'de' ist unbekannt und muss erst konfiguriert werden"
        "remittancevoucher": "false",
        "notes": "",
        "terms": "0",
        "typeofcontact": "company",
    }
    
    if customer_doc.customer_primary_contact:
        contact = frappe.get_doc("Contact", customer_doc.customer_primary_contact)
        data["salutation"] = contact.salutation
        data["firstname"] = contact.first_name
        data["lastname"] = contact.last_name
        data["phone"] = contact.phone
        data["mobile"] = contact.mobile_no
        data["email"] = contact.email_id
    
    if customer_doc.customer_primary_address:
        address = frappe.get_doc("Address", customer_doc.customer_primary_address)
        data["address1"] = address.address_line1
        data["address2"] = address.address_line2
        data["zipcode"] = address.pincode
        data["city"] = address.city
        data["state"] = address.state
        data["country"] = address.country
        
    # post the record
    post_customer(data, debug)
    
    return
    
# this function will write the record to the API
def post_customer(customer_data, debug=False):
    # read config
    config = frappe.get_doc("RunMyAccounts Settings", "RunMyAccounts Settings")
    # set enpoint
    if cint(config.test_env) == 1:
        host = TEST_HOST
    else:
        host = LIVE_HOST
    endpoint = "{host}/api/latest/clients/{mandant}/customers".format(
        host=host, mandant=config.mandant, api_key=config.api_key)
    if debug:
        print("Endpoint: {0}".format(endpoint))
    headers = {
        'X-RMA-KEY': config.api_key,
        'Content-Type': 'application/json'
    }
    # post data
    data = json.dumps(customer_data)
    r = requests.post(endpoint, data=data, headers=headers)
    # log
    log_transfer(function="post_customer", payload=data, response=r.text, status=r.status_code)
    return

# create invoice
@frappe.whitelist()
def create_invoice(sales_invoice, debug=False):
    if cint(frappe.get_value("RunMyAccounts Settings", "RunMyAccounts Settings", "enabled")) == 0:
        print("RunMyAccounts is disabled")
        return
        
    sinv_doc = frappe.get_doc("Sales Invoice", sales_invoice)
    
    # prepare data structure (see https://www.runmyaccounts.ch/support-artikel/invoice-entity/)
    data = {
        "invnumber": sinv_doc.name,
        "ordnumber": sinv_doc.items[0].sales_order or "",
        "status": sinv_doc.status,
        "transdate": sinv_doc.posting_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "duedate": sinv_doc.due_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "currency": sinv_doc.currency,
        "ar_accno": sinv_doc.debit_to[:4],
        "notes": sinv_doc.terms,
        "taxincluded": "false",
        "customer": {
            "id": sinv_doc.customer,
            "customernumber": sinv_doc.customer,
            "name": sinv_doc.customer_name
        }
    }
    
    if sinv_doc.esr_reference:
        data["dcn"] = sinv_doc.esr_reference
    
    """ disabled accounting interface version
    data["incomeentries"] = []
    data["taxentries"] = []
    # add item positions
    if cint(frappe.get_value("RunMyAccounts Settings", "RunMyAccounts Settings", "single_item")) == 1:
        # this is a hack because the items interface at RunMyAccounts is broken and will only import the last item
        data["incomeentries"].append({
                "incomeentry": {
                    "amount": sinv_doc.net_total,
                    "income_accno": sinv_doc.items[0].income_account[:4],
                    "description": "Sammelposition"
                }
            })
    else:
        # this is technically correct
        for item in sinv_doc.items:
            data["incomeentries"].append({
                "incomeentry": {
                    "amount": item.amount,
                    "income_accno": item.income_account[:4],
                    "description": item.item_code
                }
            })
    
    # add tax entries
    for tax in sinv_doc.taxes:
        data["taxentries"].append({
            "taxentry": {
                "amount": tax.tax_amount,
                "tax_accno": tax.account_head[:4]
            }
        })
    """
    
    # use part-base interface
    data["parts"] = []
    if cint(frappe.get_value("RunMyAccounts Settings", "RunMyAccounts Settings", "single_item")) == 1:
        if "302" in sinv_doc.taxes_and_charges:
            # local
            item = "3000"
        else:
            # export
            item = "3001"
        data["parts"].append({
                    "part": {
                        "partnumber": item,
                        "description": "Sammelposition",
                        "quantity": 1,
                        "sellprice": sinv_doc.net_total
                    }
                })
    else:
        for i in sinv_doc.items:
            # retrofit: this is a custom-built retrofit to match RunMyAccounts items, otherwise taxation does not work
            if "302" in sinv_doc.taxes_and_charges:
                # local
                if "AA-LIEF" in i.item_code:
                    item = "3401"
                else:
                    item = "3000"
            else:
                # export
                if "AA-LIEF" in i.item_code:
                    item = "3402"
                else:
                    item = "3001"
            data["parts"].append({
                    "part": {
                        "partnumber": item,
                        "description": i.item_name,
                        "quantity": i.qty,
                        "sellprice": i.rate,
                        "unit": i.uom
                    }
                })
            
        # this would be the correct way
        """data["parts"].append({
                "part": {
                    "partnumber": i.item_code,
                    "description": i.item_name,
                    "quantity": i.qty,
                    "sellprice": i.rate
                }
            })
        """
            
    if sinv_doc.contact_person:
        contact = frappe.get_doc("Contact", sinv_doc.contact_person)
        data["customer"]["salutation"] = contact.salutation
        data["customer"]["firstname"] = contact.first_name
        data["customer"]["lastname"] = contact.last_name
        data["customer"]["phone"] = contact.phone
        data["customer"]["mobile"] = contact.mobile_no
        data["customer"]["email"] = contact.email_id
    
    if sinv_doc.customer_address:
        address = frappe.get_doc("Address", sinv_doc.customer_address)
        data["customer"]["address1"] = address.address_line1
        data["customer"]["address2"] = address.address_line2
        data["customer"]["zipcode"] = address.pincode
        data["customer"]["city"] = address.city
        data["customer"]["state"] = address.state
        data["customer"]["country"] = address.country
        
    # post the record (json)
    status = post_sales_invoice(data, debug)

    # retrofit to xml
    """
    xml = frappe.render_template("/templates/includes/rma_invoice.html", data)
    status = post_sales_invoice_soap(xml, debug)
    """
    
    # close invoice in ERP
    if cint(frappe.get_value("RunMyAccounts Settings", "RunMyAccounts Settings", "close_invoice_automatically")) == 1: # and status == 204
        create_payment_entry(
            customer=sinv_doc.customer,
            date=datetime.now(), 
            to_account=frappe.get_value("RunMyAccounts Settings", "RunMyAccounts Settings", "invoice_account"), 
            received_amount=sinv_doc.outstanding_amount, 
            reference=sinv_doc.name, 
            remarks="Auto RunMyAccounts", 
            auto_submit=True
        )
        
    return

# create a payment entry
def create_payment_entry(customer, date, to_account, received_amount, reference, remarks, auto_submit=False):
    # create new payment entry
    new_payment_entry = frappe.get_doc({
        'doctype': 'Payment Entry',
        'payment_type': "Receive",
        'party_type': "Customer",
        'party': customer,
        'posting_date': date,
        'paid_to': to_account,
        'received_amount': received_amount,
        'paid_amount': received_amount,
        'reference_no': reference,
        'reference_date': date,
        'remarks': remarks,
        'references': [{
            'reference_doctype': "Sales Invoice",
            'reference_name': reference,
            'outstanding_amount': received_amount,
            'allocated_amount': received_amount
        }]
    })

    inserted_payment_entry = new_payment_entry.insert()
    if auto_submit:
        new_payment_entry.submit()
    frappe.db.commit()
    return inserted_payment_entry
        
# this function will write the sales invoice to the API
def post_sales_invoice(sinv_data, debug=False):
    # read config
    config = frappe.get_doc("RunMyAccounts Settings", "RunMyAccounts Settings")
    # set enpoint
    if cint(config.test_env) == 1:
        host = TEST_HOST
    else:
        host = LIVE_HOST
    endpoint = "{host}/api/latest/clients/{mandant}/invoices".format(
        host=host, mandant=config.mandant, api_key=config.api_key)
    if debug:
        print("Endpoint: {0}".format(endpoint))
    headers = {
        'X-RMA-KEY': config.api_key,
        'Content-Type': 'application/json'
    }
    # post data
    data = json.dumps(sinv_data)
    r = requests.post(endpoint, data=data, headers=headers)
    # log
    log_transfer(function="post_sales_invoice", payload=data, response=r.text, status=r.status_code)
    return r.status_code

# this function will write the sales invoice to the API
def post_sales_invoice_soap(sinv_data, debug=False):
    # read config
    config = frappe.get_doc("RunMyAccounts Settings", "RunMyAccounts Settings")
    # set enpoint
    if cint(config.test_env) == 1:
        host = TEST_HOST
    else:
        host = LIVE_HOST
    endpoint = "{host}/api/latest/clients/{mandant}/invoices".format(
        host=host, mandant=config.mandant, api_key=config.api_key)
    if debug:
        print("Endpoint: {0}".format(endpoint))
    headers = {
        'X-RMA-KEY': config.api_key,
        'Content-Type': 'application/xml',
        'Host': host.split("//")[-1],
        'Content-Length': str(len(sinv_data))
    }
    # post data
    r = requests.post(endpoint, data=sinv_data, headers=headers)
    # log
    log_transfer(function="post_sales_invoice_soap", payload=sinv_data, response=r.text, status=r.status_code)
    return r.status_code
    
def log_transfer(function, payload, response, status):
    log = frappe.get_doc({
        'doctype': "RunMyAccounts Log",
        'date': datetime.now(),
        'function': function,
        'payload': "{0}".format(payload),
        'response': "{0}".format(response),
        'status': status
    })
    log.insert(ignore_permissions=True)
    frappe.db.commit()
    return
    
# document hooks
def create_customer_hook(customer, method):
    if frappe.db.exists("Customer", customer.name):
        create_customer(customer)
    return
    
def submit_sales_invoice_hook(sales_invoice, method):
    create_invoice(sales_invoice.name)
    return

# migration patterns
def prepare_customers():
    # this function will set the primary address field for the customer if empty
    from erpnextswiss.scripts.crm_tools import get_primary_customer_address, get_primary_customer_contact
    all_customers = frappe.get_all("Customer", filters={'disabled': 0}, fields=['name', 'customer_primary_address', 'customer_primary_contact'])
    
    for customer in all_customers:
        if customer['customer_primary_address']:
            print("Skipping {0} address...".format(customer['name']))
        else:
            address = get_primary_customer_address(customer['name'])
            if address:
                doc = frappe.get_doc("Customer", customer['name'])
                doc.customer_primary_address = address.name
                doc.save()
                print("Updated {0} address".format(customer['name']))
        
        if customer['customer_primary_contact']:
            print("Skipping {0} contact...".format(customer['name']))
        else:
            contact = get_primary_customer_contact(customer['name'])
            if contact:
                doc = frappe.get_doc("Customer", customer['name'])
                doc.customer_primary_contact = contact.name
                doc.save()
                print("Updated {0} contact".format(customer['name']))
    return
    
def send_all_customers():
    all_customers = frappe.get_all("Customer", filters={'disabled': 0}, fields=['name'])
    
    for customer in all_customers:
        create_customer(customer['name'])
        print("Created {0}".format(customer['name']))
    
    print("Uploaded {0} customers".format(len(all_customers)))
    
    return

def send_invoices(from_date):
    invoices = frappe.get_all("Sales Invoice", 
        filters=[['docstatus', '=', 1], ['posting_date', '>=', from_date]],
        fields=['name']
    )
    
    for sales_invoice in invoices:
        create_invoice(sales_invoice['name'])
        print("Created {0}".format(sales_invoice['name']))
    
    print("Uploaded {0} sales_invoice".format(len(invoices)))
