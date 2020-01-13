# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import pdfkit, os, frappe
from frappe.model.document import Document

# creates a pdf based on a label printer and a html content
def create_dn_pdf(label_printer, delivery_note):
    # create temporary file
    fname = os.path.join("/tmp", "frappe-pdf-{0}.pdf".format(frappe.generate_hash()))

    options = {
        'page-width': '{0}mm'.format(label_printer.width),
        'page-height': '{0}mm'.format(label_printer.height),
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm' }

    dn = frappe.get_doc("Delivery Note", delivery_note)
    items = []
    for item in dn.items:
        drawing_no = frappe.get_value("Item", item.item_code, "drawing_no")
        description = None
        if item.item_code not in item.description and item.item_name not in item.description:
            description = item.description
        items.append({
            'against_sales_order': item.against_sales_order,
            'item_name': item.item_name,
            'item_code': item.item_code,
            'drawing_no': drawing_no,
            'qty': item.qty,
            'description': description
        })
    data = {
        'customer': dn.customer,
        'customer_name': dn.customer_name,
        'po_no': dn.po_no,
        'items': items
    }
    html_content = frappe.render_template('kuchelmeister/templates/labels/dn_label.html', data)
    pdfkit.from_string(html_content, fname, options=options or {})
    with open(fname, "rb") as fileobj:
        filedata = fileobj.read()
    cleanup(fname)
    return filedata

# creates a pdf based on a label printer and a html content
def create_so_pdf(label_printer, sales_order):
    # create temporary file
    fname = os.path.join("/tmp", "frappe-pdf-{0}.pdf".format(frappe.generate_hash()))

    options = {
        'page-width': '{0}mm'.format(label_printer.width),
        'page-height': '{0}mm'.format(label_printer.height),
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm' }

    so = frappe.get_doc("Sales Order", sales_order)
    items = []
    for item in so.items:
        drawing_no = frappe.get_value("Item", item.item_code, "drawing_no")
        description = None
        if item.item_code not in item.description and item.item_name not in item.description:
            description = item.description
        items.append({
            'against_sales_order': sales_order,
            'item_name': item.item_name,
            'item_code': item.item_code,
            'drawing_no': drawing_no,
            'qty': item.qty,
            'description': description
        })
    data = {
        'customer': so.customer,
        'customer_name': so.customer_name,
        'po_no': so.po_no,
        'items': items
    }
    html_content = frappe.render_template('kuchelmeister/templates/labels/dn_label.html', data)
    pdfkit.from_string(html_content, fname, options=options or {})
    with open(fname, "rb") as fileobj:
        filedata = fileobj.read()
    cleanup(fname)
    return filedata

def cleanup(fname):
    if os.path.exists(fname):
        os.remove(fname)
    return

@frappe.whitelist()
def download_label(label_reference, dn, name=None, dt="Delivery Note"):
    label = frappe.get_doc("Label Printer", label_reference)
    frappe.local.response.filename = "{name}.pdf".format(name=(name or label_reference.replace(" ", "-").replace("/", "-")))
    if dt == "Delivery Note":
        frappe.local.response.filecontent = create_dn_pdf(label, dn)
    else:
        frappe.local.response.filecontent = "Invalid output type"
    frappe.local.response.type = "download"
