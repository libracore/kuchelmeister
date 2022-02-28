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
    endpoint = "https://service.int.runmyaccounts.com/api/latest/clients/{mandant}/customers".format(
        mandant=config.mandant, api_key=config.api_key)
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
    
    # prepare data structure (see https://www.runmyaccounts.ch/support-artikel/customer-entity/)
    data = {
        "invnumber": sinv_doc.name,
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
        },
        "incomeentries": [],
        "taxentries": []
    }
    
    # add item positions
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
        
    # post the record
    post_sales_invoice(data, debug)
    
    return

# this function will write the sales invoice to the API
def post_sales_invoice(sinv_data, debug=False):
    # read config
    config = frappe.get_doc("RunMyAccounts Settings", "RunMyAccounts Settings")
    # set enpoint
    endpoint = "https://service.int.runmyaccounts.com/api/latest/clients/{mandant}/invoices".format(
        mandant=config.mandant, api_key=config.api_key)
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
    return
    
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
