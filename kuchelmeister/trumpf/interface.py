# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
#
import frappe           # for frappe framework
import codecs           # for utf-8 encoding
import cgi              # for xml escaping
import hashlib          # for md5 hashes
import os               # for file handling
from frappe.desk.form.load import get_attachments
from frappe.utils import get_url

@frappe.whitelist()
def write_item(item_code):
    item = frappe.get_doc("Item", item_code)
    settings = frappe.get_doc("Trumpf Settings")
    target_path = settings.physical_path
    # create a unique item code, limited to 21 characters based on md5 hash
    trumpf_item_code = hashlib.md5(item_code.encode('utf-8')).hexdigest()[:21]
    if item.material:
        material = cgi.escape(item.material)
    else:
        material = None
    attachments = get_attachments(dt="Item", dn=item_code)
    if attachments and len(attachments) > 0:
        documents = []
        for attachment in attachments:
            documents.append({
                'url': get_url(attachment['file_url']),
                'name': attachment['name'],
                'filename': attachment['file_name']
            })
    else:
        documents = None
    data = {
        'item_code': cgi.escape(item_code),
        'trumpf_item_code': trumpf_item_code,
        'description': cgi.escape(item.description),
        'item_group': cgi.escape(item.item_group),
        'material': material,
        'default_uom': item.stock_uom,
        'documents': documents,
        'prices': None
    }
    content = frappe.render_template('kuchelmeister/trumpf/item.html', data)
    file = codecs.open("{path}MasterDataImp{item_code}.xml".format(path=target_path,
        item_code=item_code), "w", "utf-8")
    file.write(content)
    file.close()
    # update item
    item.trumpf_fab_opened = 1                  # mark as exported
    item.trumpf_item_code = trumpf_item_code    # store Trumpf item code
    item.save()
    return

@frappe.whitelist()
def check_fab_items(sales_order_name):
    sales_order = frappe.get_doc("Sales Order", sales_order_name)
    items = []
    for i in sales_order.items:
        item_record = frappe.get_doc("Item", i.item_code)
        if item_record.trumpf_fab_opened == 1 and item_record.trumpf_item_code:
            items.append({
                'item_code': item_record.item_code,
                'item_name': item_record.item_name,
                'status': 'OK'
            })
        else:
            items.append({
                'item_code': item_record.item_code,
                'item_name': item_record.item_name,
                'status': 'Not in FAB'
            })
    message = frappe.render_template('kuchelmeister/trumpf/sales_order_item_status.html', {'items': items})
    return {'items': items, 'message': message}

@frappe.whitelist()
def write_production_order(sales_order_name):
    sales_order = frappe.get_doc("Sales Order", sales_order_name)
    settings = frappe.get_doc("Trumpf Settings")
    target_path = settings.physical_path
    # collect items
    items = []
    for i in sales_order.items:
        item_record = frappe.get_doc("Item", i)
        if item_record.trumpf_fab_opened == 1 and item_record.trumpf_item_code:
            if item_record.material:
                material = cgi.escape(item_record.material)
            else:
                material = None
            if item_record.drawing_no:
                drawing_no = cgi.escape(item_record.drawing_no)
            else:
                drawing_no = None
            items.append({
                'item_code': item_record.item_code,
                'item_name': cgi.escape(item_record.item_name),
                'trumpf_item_code': item_record.trumpf_item_code,
                'qty': item_record.qty,
                'drawing_no': drawing_no,
                'material': material
            })            
    attachments = get_attachments(dt="Item", dn=item_code)
    if attachments and len(attachments) > 0:
        documents = []
        for attachment in attachments:
            documents.append({
                'url': get_url(attachment['file_url']),
                'name': attachment['name'],
                'filename': attachment['file_name']
            })
    else:
        documents = None
    data = {
        'po_no': sales_order.po_no,
        'customer': sales_order.customer,
        'customer_name': cgi.escape(sales_order.customer_name),
        'sales_order': sales_order.name,
        'items': items
    }
    content = frappe.render_template('kuchelmeister/trumpf/item.html', data)
    file = codecs.open("{path}MasterDataImp{item_code}.xml".format(path=target_path,
        item_code=item_code), "w", "utf-8")
    file.write(content)
    file.close()
    # update item
    item.trumpf_fab_opened = 1                  # mark as exported
    item.trumpf_item_code = trumpf_item_code    # store Trumpf item code
    item.save()
    return
