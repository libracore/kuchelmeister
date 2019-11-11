# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Import using
#  $ bench execute kuchelmeister.utils.import.import_sinv_docs --kwargs "{'f': '/home/frappe/sinv.csv'}"
#  $ bench execute kuchelmeister.utils.import.import_sinv_pos --kwargs "{'f': '/home/frappe/sinv_pos.csv'}"
#  $ bench execute kuchelmeister.utils.import.import_sinv_docs --kwargs "{'f': '/home/frappe/sinv.csv'}"
#
import frappe
import csv
import uuid

# import sales invoices
def import_sinv_docs(f):
    DOCNAME = 0
    CUSTOMER = 1
    NAMINGSERIES = 2 
    COMPANY = 3 
    DATE = 4 
    CURRENCY = 5
    PRICELIST = 6
    DEBITTO = 7
    
    # clear all records
    print("WARNING: clearing all sales invoices")
    frappe.db.sql("""DELETE FROM `tabSales Invoice` WHERE `name` LIKE '%';""")
    # read csv file
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        counter = 0
        for row in csv_reader:
            if counter > 0:
                # for each line, create a document
                name = row[DOCNAME]
                customer = "K-{0:05d}".format(int(row[CUSTOMER]))
                naming_series = row[NAMINGSERIES]
                company = row[COMPANY]
                posting_date = row[DATE] 
                currency = row[CURRENCY] 
                selling_price_list = row[PRICELIST]
                debit_to = row[DEBITTO]
                sql = """INSERT INTO `tabSales Invoice` 
                    (`name`, 
                     `customer`, 
                     `docstatus`,
                     `naming_series`, 
                     `company`, 
                     `posting_date`, 
                     `currency`, 
                     `selling_price_list`, 
                     `price_list_currency`, 
                     `debit_to`)
                    VALUES ('{name}', 
                     '{customer}', 
                     1,
                     '{naming_series}', 
                     '{company}', 
                     '{posting_date}', 
                     '{currency}', 
                     '{selling_price_list}', 
                     '{currency}', 
                     '{debit_to}');""".format(
                    name=name, 
                    customer=customer,
                    naming_series=naming_series,
                    company=company, 
                    posting_date=posting_date, 
                    currency=currency, 
                    selling_price_list=selling_price_list, 
                    debit_to=debit_to)
                print(sql)
                print("Creating {0} for customer {1} ({2})".format(name, customer, counter))
                frappe.db.sql(sql)
            counter += 1
    frappe.db.commit()
    
def import_sinv_pos(f):
    # read pos csv file
    DOCNAME = 0
    ITEM = 1
    QTY = 2
    RATE = 3
    INCOME = 4
    KST = 5
    # clear all records
    print("WARNING: clearing all sales invoice items")
    frappe.db.sql("""DELETE FROM `tabSales Invoice Item` WHERE `name` LIKE '%';""")
    # read csv file
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        counter = 0
        for row in csv_reader:
            if counter > 0:
                # for each line, add a position record
                parent = row[DOCNAME]
                item = row[ITEM]
                qty = row[QTY]
                rate = row[RATE]
                i = frappe.get_doc("Item", item)
                income = row[INCOME]
                kst = row[KST]
                sql = """INSERT INTO `tabSales Invoice Item` 
                    (`name`, `parent`, `parentfield`, `parenttype`, 
                    `item_code`, `qty`, `rate`,
                    `item_name`, `description`, `uom`, `income_account`, `cost_center`)
                    VALUES ('{name}', '{parent}', 'items', 'Sales invoice', 
                    '{item_code}', qty, rate,
                    '{item_name}', '{description}', '{uom}', '{income}', '{kst}');""".format(
                    name=uuid.uuid4().hex, parent=parent, 
                    item_code=item, qty=qty, rate=rate,
                    item_name=i.item_name, description=i.description, uom=i.stock_uom, income=income, kst=kst)
                print("Creating item {0} for sales invoice {1}".format(item, parent))
                frappe.db.sql(sql)
            counter += 1
    frappe.db.commit()    
    
def consolidate_sinvs():
    # consolidate sinv records
    sinvs = frappe.get_all("Sales Invoice", filters={'docstatus': 1}, fields=['name'])
    for sinv in sinvs:
        print("Consolidating {0}".format(sinv['name']))
        record = frappe.get_doc("Sales Invoice", sinv['name'])
        record.save()
        frappe.db.commit()
