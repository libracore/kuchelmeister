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
from bs4 import BeautifulSoup    # xml parser
from datetime import date

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
        cad_file_name = None
        for attachment in attachments:
            if attachment['is_private'] == 0:
                documents.append({
                    'url': "{0}{1}".format(settings.smb_path, attachment['file_name']),
                    'name': attachment['name'],
                    'filename': attachment['file_name']
                })
            # GEO files override other drawing types
            if attachment['file_name'].endswith(".geo"):
                cad_file_name = "{0}{1}".format(settings.smb_path, attachment['file_name'])
            # attach other drawing types if empty
            if (attachment['file_name'].endswith(".dxf") or attachment['file_name'].endswith(".dxg") or attachment['file_name'].endswith(".step")) and cad_file_name == None:
                cad_file_name = "{0}{1}".format(settings.smb_path, attachment['file_name'])
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
        'prices': None,
        'cad_file_name': cad_file_name
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
    # add log
    add_log(title="Item sent to FAB", message="Item: {item_code}".format(item_code=item_code))
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
        item_record = frappe.get_doc("Item", i.item_code)
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
                'qty': i.qty,
                'drawing_no': drawing_no,
                'material': material,
                'order_code': "{0}/{1}".format(sales_order_name, i.idx)
            })            
    attachments = get_attachments(dt="Sales Order", dn=sales_order_name)
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
        'items': items,
        'delivery_date': "{day:2d}.{month:2d}.{year:4d} 00:00".format(
            day=sales_order.delivery_date.day,
            month=sales_order.delivery_date.month,
            year=sales_order.delivery_date.year)
    }
    content = frappe.render_template('kuchelmeister/trumpf/production_order.html', data)
    file = codecs.open("{path}ProdOrderImp{sales_order}.xml".format(path=target_path,
        sales_order=sales_order_name), "w", "utf-8")
    file.write(content)
    file.close()
    # add log
    add_log(title="Sales Order sent to FAB", message="Sales Order: {sales_order_name}".format(
        sales_order_name=sales_order_name))
    return

@frappe.whitelist()
def cancel_production_order(sales_order_name):
    settings = frappe.get_doc("Trumpf Settings")
    target_path = settings.physical_path
    order_codes = []
    so = frappe.get_doc("Sales Order", sales_order_name)
    for i in sales_order.items:
        order_codes.append("{0}/{1}".format(sales_order_name, i.idx))
    data = {
        'order_codes': order_codes
    }
    content = frappe.render_template('kuchelmeister/trumpf/cancel_production_order.html', data)
    file = codecs.open("{path}DelProdOrderImp{sales_order}.xml".format(path=target_path,
        sales_order=sales_order_name), "w", "utf-8")
    file.write(content)
    file.close()
    return

# this function will import a file from FAB    
def import_file(filename):
    # read the file
    f = open(filename, "r")
    content = f.read()
    f.close()
    # check the content for content types
    if "ProductionOrderFeedback" in content:
        import_production_order_status(content)
    # ..extend here..
    
    # move the file to archive
    settings = frappe.get_doc("Trumpf Settings")
    name = filename.split('/')[-1]
    archive_filename = settings.archive_path + name
    os.rename(filename, archive_filename)
    return

# this function will parse production order status information
def import_production_order_status(content):
    # prepare content
    soup = BeautifulSoup(content, 'lxml')
    production_orders = soup.find_all('productionorder')
    for po in production_orders:
        part_no = po.partno.get_text()
        order_code = po['orderno']
        sales_order = order_code.split('/')[0]
        pos = int(order_code.split('/')[1])
        return_code = int(po.returncode.get_text())
        description = po.description.get_text()
        
        # make return code human readable
        return_status = "unclear"
        if return_code == 10:
            return_status = "Completed"
        elif return_code == 0:
            return_status = "OK"
        elif return_code == 30:
            return_status = "Step done"
            
        # set item status
        so = frappe.get_doc("Sales Order", sales_order)
        so.items[pos - 1].fab_status = "{0}: {1} ({2})".format(date.today(), return_code, return_status)
        so.save()
        
        # insert comment and pull last save date forward
        comment="""Position: {pos}
                   Return code: {rc} ({rs})""".format(
            pos=pos,
            rc=return_code,
            rs=return_status)
        """new_comment = frappe.get_doc({
            'doctype': 'Communication',
            'comment_type': 'Comment',
            'content': comment,
            'reference_doctype': 'Sales Order',
            'status': 'Linked',
            'reference_name': sales_order,
            'owner': 'Administrator'
        })
        new_comment.insert()"""
        frappe.db.commit()
        
        # add log
        add_log(title="Sales Order Status from FAB", 
            message="""Sales Order: {sales_order}, 
                       Position: {pos}
                       Return code: {rc} ({rs})""".format(
            sales_order=sales_order,
            pos=pos,
            rc=return_code,
            rs=return_status))
        
    return
        
# this function scans the share folder for new *Exp*.xml files    
def check_exchange_folder():
    settings = frappe.get_doc("Trumpf Settings")
    files = []
    for f in os.listdir(settings.physical_path):
        full_name = os.path.join(settings.physical_path, f)
        if os.path.isfile(full_name):
            files.append(full_name)
    for f in files:
        if "Exp" in f and "xml" in f:
            import_file(f)
    return

# add log
def add_log(title, message):
    l = frappe.get_doc({
        'doctype': 'Trumpf Log',
        'title': title,
        'message': message,
        'date': date.today()
    })
    l.insert()
    frappe.db.commit()
    return
