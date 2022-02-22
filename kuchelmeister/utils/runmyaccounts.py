# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
import frappe
from frappe import _
import urllib.request
import requests
import json
from datetime import date, timedelta

# create customer
@frappe.whitelist()
def create_customer(customer):
    customer_doc = frappe.get_doc("Customer", customer)
    
    # prepare data structure (see https://www.runmyaccounts.ch/support-artikel/customer-entity/)
    data = {
        "customernumber": customer_doc.name,
        "name": customer_doc.customer_name[:64],
        "created": customer_doc.creation.strftime("%Y-%m-%dT%H:%M:%S"),
        "language_code": customer_doc.language,
        "remittancevoucher": "false",
        "notes": "",
        "terms": "0",
        "typeofcontact": "company",
    }
    
    if customer_doc.customer_primary_contact:
        contact = frappe.get_doc("Contact", customer_doc.customer_primary_contact)
        data["salutation"] = contact.salutation
        data["firstname"] = contact.frist_name
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
    post_customer(data)
    
    return
    
# this function will write the record to the API
def post_customer(customer_data):
    # read config
    config = frappe.get_doc("RunMyAccounts Settings", "RunMyAccounts Settings")
    # set enpoint
    endpoint = "https://service.runmyaccounts.com/api/latest/clients/{mandant}/customers?api_key={api_key}".format(
        mandant=config.mandant, api_key=config.api_key)
    # post data
    r = requests.post(endpoint, data=customer_data)
    # log
    log_transfer(function="post_customer", payload=customer_data, response=r.text, status=r.status_code)
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
    frappe.db.submit()
    return
    
