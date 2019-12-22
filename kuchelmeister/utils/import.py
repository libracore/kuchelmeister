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
def import_sinv_docs(f, clear=False):
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
    if clear:
        print("WARNING: clearing all sales invoices")
        frappe.db.sql("""DELETE FROM `tabSales Invoice` WHERE `name` LIKE '%';""")
        frappe.db.sql("""DELETE FROM `tabSales Taxes and Charges` WHERE `parenttype` = 'Sales Invoice';""")
    # read csv file
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        counter = 0
        for row in csv_reader:
            if counter > -1:
                # for each line, create a document
                name = row[DOCNAME]
                customer = row[CUSTOMER]
                naming_series = row[NAMINGSERIES]
                company = row[COMPANY]
                posting_date = row[DATE] 
                currency = row[CURRENCY] 
                selling_price_list = row[PRICELIST]
                debit_to = row[DEBITTO]
                tax_account = row[TAXACCOUNT]
                tax_amount = row[TAXAMOUNT]
                kst = row[KST]
                terms = row[TERMS].replace("'", "`")
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
    
def import_sinv_pos(f, clear=False):
    # read pos csv file
    DOCNAME = 0
    ITEM = 1
    QTY = 2
    RATE = 3
    INCOME = 4
    KST = 5
    DESCRIPTION = 6
    # clear all records
    if clear:
        print("WARNING: clearing all sales invoice items")
        frappe.db.sql("""DELETE FROM `tabSales Invoice Item` WHERE `name` LIKE '%';""")
    # read csv file
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        counter = 0
        for row in csv_reader:
            if counter > -1:
                # for each line, add a position record
                parent = row[DOCNAME]
                item = row[ITEM].replace("'", "`")
                qty = row[QTY]
                rate = row[RATE]
                if frappe.db.exists("Item", item):
                    i = frappe.get_doc("Item", item)
                    income = row[INCOME]
                    kst = row[KST]
                    description = row[DESCRIPTION].replace("'", "`")
                    sql = """INSERT INTO `tabSales Invoice Item` 
                        (`name`, `parent`, `parentfield`, `parenttype`, 
                        `item_code`, `qty`, `rate`,
                        `item_name`, `description`, `uom`, `income_account`, `cost_center`)
                        VALUES ('{name}', '{parent}', 'items', 'Sales Invoice', 
                        '{item_code}', {qty}, {rate},
                        '{item_name}', '{description}', '{uom}', '{income}', '{kst}');""".format(
                        name=uuid.uuid4().hex, parent=parent, 
                        item_code=item, qty=qty, rate=rate,
                        item_name=i.item_name, description=description, uom=i.stock_uom, income=income, kst=kst)
                    print(sql)
                    print("Creating item {0} for sales invoice {1}".format(item, parent))
                    frappe.db.sql(sql)
                    frappe.db.commit()
                else:
                    print("{0} is not a known item".format(item))
            counter += 1
    
def consolidate_sinvs(bank_account="Bank"):
    # consolidate sinv records
    sinvs = frappe.get_all("Sales Invoice", filters={'docstatus': 0}, fields=['name'])
    for sinv in sinvs:
        print("Consolidating {0}".format(sinv['name']))
        try:
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
                'paid_amount': record.outstanding_amount,
                'reference_no': record.name,
                'reference_date': record.due_date
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
        except Exception as e:
            print("Failed: {0}".format(e))

# update items
def update_items(f):
    # read item csv file
    ITEMCODE = 0
    SKU = 1
    ITEMNAME = 2
    # read csv file
    counter = 0
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        for row in csv_reader:
          print(row)
          if counter > 0:
            item_code = row[ITEMCODE].strip()
            item_name = row[ITEMNAME].strip()
            try:
                sku_code = int(row[SKU])
            except:
                sku_code = 0
            if sku_code == 3 or sku_code == 1:
                sku = "Stk"
            elif sku_code == 10:
                sku = "L"
            elif sku_code == 2:
                sku = "m2"
            elif sku_code == 4:
                sku = "kg"
            elif sku_code == 5:
                sku = "h"
            elif sku_code == 7:
                sku = "Rolle"
            elif sku_code == 8:
                sku = "km"
            elif sku_code == 9:
                sku = "m"
            else:
                sku = "Stk"
            if not frappe.db.exists("Item", item_code):
                # create item
                new_item = frappe.get_doc({
                    'doctype': 'Item',
                    'item_code': item_code,
                    'item_name': item_name,
                    'stock_sku': sku,
                    'item_group': "Allgemein",
                    'is_stock_item': 0,
                    'include_item_in_manufacturing': 0
                })
                new_item.insert()
                frappe.db.commit()
                print("Inserted {0}".format(item_code))
            else:
                print("Skipping {0}".format(item_code))
          counter += 1
    print("Done with {0} items".format(counter))
    return

# update items
def update_customers(f):
    # read item csv file
    CUSTOMER = 0
    CUSTOMER_NAME = 1
    STREET = 2
    CITY = 3
    PINCODE = 4
    PHONE = 5
    # read csv file
    counter = 0
    with open(f) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        for row in csv_reader:
          print(row)
          if counter > 0:
            customer = "K-{0:05d}".format(int(row[CUSTOMER].strip()))
            customer_name = row[CUSTOMER_NAME].strip()
            description = "{0}, {1} {2}, {3}".format(row[STREET], row[PINCODE], row[CITY], row[PHONE])

            if not frappe.db.exists("Customer", customer):
                # create customer
                new_customer = frappe.get_doc({
                    'doctype': 'Customer',
                    'name': customer,
                    'customer_details': customer,
                    'customer_name': customer_name,
                    'customer_group': 'Alle Kundengruppen',
                    'territory': 'CH',
                    'type': 'Company',
                    'naming-series': 'K-.#####'
                })
                new_customer.insert()
                frappe.db.commit()
                print("Inserted {0}".format(customer))
            else:
                print("Skipping {0}".format(customer))
          counter += 1
    print("Done with {0} customers".format(counter))
    return
