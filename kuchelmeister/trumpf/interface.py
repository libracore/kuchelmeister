# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
#
import frappe           # for frappe framework
import codecs           # for utf-8 encoding
import cgi              # for xml escaping
import hashlib          # for md5 hashes
from frappe.desk.form.load import get_attachments

def write_item(item_code):
    item = frappe.get_doc("Item", item)
    target_path = frappe.get_value("Trumpf Settings", "Trumpf Settings", "physical_path", ignore_permissions=True)
    # create a unique item code, limited to 21 characters based on md5 hash
    trumpf_item_code = hashlib.md5(item_code.encode('utf-8')).hexdigest()[:21]
    if item.material:
        material = cgi.escape(item.material)
    else:
        material = None
    if item.attachments:
        documents = []
        for attachment in get_attachments(dt="Item", dn=item_code):
            documents.append({
                'path': attachment['file_url'],
                'name': attachment['name']
            })
    else:
        documents = None
    data = {
        'item_code': cgi.escape(item_code),
        'trumpf_item_code': trumpf_item_code
        'description': cgi.escape(item.description),
        'item_group': cgi.escape(item.item_group),
        'material': material,
        'default_uom': item.stock_uom,
        'documents': documents,
        'prices': None
    }
    content = frappe.render_template('kuchelmeister/trumpf/item.html', data)
    file = codecs.open("MasterDataImp{item_code}.xml".format(item_code), "w", "utf-8")
    file.write(content)
    file.close()
    return

