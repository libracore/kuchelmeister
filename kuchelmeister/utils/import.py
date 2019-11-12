# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Import using
#  $ bench execute kuchelmeister.utils.import.import_sinv_docs --kwargs "{'f': '/home/frappe/sinv.csv'}"
#  $ bench execute kuchelmeister.utils.import.import_sinv_pos --kwargs "{'f': '/home/frappe/sinv_pos.csv'}"
#  $ bench execute kuchelmeister.utils.import.consolidate_sinvs --kwargs "{'bank_account': 'Bank'}"
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
    TAXACCOUNT = 8
    TAXAMOUNT = 9
    KST = 10
    TERMS = 11
    # clear all records
    print("WARNING: clearing all sales invoices")
    frappe.db.sql("""DELETE FROM `tabSales Invoice` WHERE `name` LIKE '%';""")
    frappe.db.sql("""DELETE FROM `tabSales Taxes and Charges` WHERE `parenttype` = 'Sales Invoice';""")
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
                tax_account = row[TAXACCOUNT]
                tax_amount = row[TAXAMOUNT]
                kst = row[KST]
                terms = row[TERMS]
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
                     `debit_to`,
                     `due_date`,
                     `title`,
                     `terms`,
                     `set_posting_time`)
                    VALUES ('{name}', 
                     '{customer}', 
                     0,
                     '{naming_series}', 
                     '{company}', 
                     '{posting_date}', 
                     '{currency}', 
                     '{selling_price_list}', 
                     '{currency}', 
                     '{debit_to}',
                     '{posting_date}',
                     '{customer}',
                     '{terms}',
                     1);""".format(
                    name=name, 
                    customer=customer,
                    naming_series=naming_series,
                    company=company, 
                    posting_date=posting_date, 
                    currency=currency, 
                    selling_price_list=selling_price_list, 
                    debit_to=debit_to,
                    terms=terms)
                #print(sql)
                print("Creating {0} for customer {1} ({2})".format(name, customer, counter))
                frappe.db.sql(sql)
                # tax section
                sql = """INSERT INTO `tabSales Taxes and Charges` 
                    (`name`, `parent`, `parentfield`, `parenttype`, 
                    `charge_type`, `account_head`, `description`,
                    `tax_amount`, `cost_center`)
                    VALUES ('{name}', '{parent}', 'taxes', 'Sales Invoice', 
                    'Actual', '{tax_account}', 'MwSt Import',
                    '{rate}', '{kst}');""".format(
                    name=uuid.uuid4().hex, parent=name, 
                    tax_account=tax_account, rate=tax_amount, kst=kst)
                print(sql)
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
                    VALUES ('{name}', '{parent}', 'items', 'Sales Invoice', 
                    '{item_code}', {qty}, {rate},
                    '{item_name}', '{description}', '{uom}', '{income}', '{kst}');""".format(
                    name=uuid.uuid4().hex, parent=parent, 
                    item_code=item, qty=qty, rate=rate,
                    item_name=i.item_name, description=i.description, uom=i.stock_uom, income=income, kst=kst)
                print(sql)
                print("Creating item {0} for sales invoice {1}".format(item, parent))
                frappe.db.sql(sql)
            counter += 1
    frappe.db.commit()    
    
def consolidate_sinvs(bank_account="Bank"):
    # consolidate sinv records
    sinvs = frappe.get_all("Sales Invoice", filters={'docstatus': 0}, fields=['name'])
    for sinv in sinvs:
        print("Consolidating {0}".format(sinv['name']))
        record = frappe.get_doc("Sales Invoice", sinv['name'])
        record.save()
        record.submit()
        # create corresponding payment
        new_payment_entry = frappe.get_doc({
            'doctype': 'Payment Entry',
            'payment_type': "Receive",
            'party_type': "Customer",
            'party': record.customer,
            'posting_date': record.due_date,
            'paid_to': bank_account,
            'received_amount': record.outstanding_amount,
            'paid_amount': record.outstanding_amount
        })
        inserted_payment_entry = new_payment_entry.insert()
        inserted_payment_entry.append('references', {
                'reference_doctype': 'Sales Invoice',
                'reference_name': record.name,
                'allocated_amount': record.outstanding_amount
            })
        inserted_payment_entry.save()
        inserted_payment_entry.submit()
        frappe.db.commit()
