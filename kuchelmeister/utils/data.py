# Copyright (c) 2016-2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def check_so_subakkordanten(sales_order):
    so = frappe.get_doc("Sales Order", sales_order)
    items = []
    for i in so.items:
        items.append(i.item_code)
    sql_query = """SELECT `parent`, `subakkordant`, `subakkordant_name`, `remarks` 
                   FROM `tabItem Subakkordant`
                   WHERE `parent` IN ('{items}');""".format(items="', '".join(items))
    data = frappe.db.sql(sql_query, as_dict=True)
    return data

""" This function will check if all stock material is available """
@frappe.whitelist()
def check_so_item_availability(sales_order):
    so = frappe.get_doc("Sales Order", sales_order)
    # build a list with all items to check
    stock_items = []
    for i in so.items:
        for expanded_item in check_item(i.item_code, i.qty):
            stock_items.append(expanded_item)
    # aggregate item list
    short_items = {}
    for i in stock_items:
        if i['item_code'] in short_items:
            short_items[i['item_code']] += i['qty']
        else:
            short_items[i['item_code']] = i['qty']
    # check availability
    availability_map = []
    for key, value in short_items.items():
        availability = check_availability(key, value)
        if availability:
            availability_map.append(availability[0])
    return availability_map
                
def check_item(item_code, qty):
    item = frappe.get_doc("Item", item_code)
    stock_items = []
    # check if item is a stock item
    if item.is_stock_item:
        # check if item has a bom
        sql_query = """SELECT `name` 
                       FROM `tabBOM` 
                       WHERE
                         `item` = '{item}'
                         AND `docstatus` = 1
                         AND `is_active` = 1
                         AND `is_default` = 1;""".format(item=item_code)
        boms = frappe.db.sql(sql_query, as_dict=True)
        if boms and len(boms) > 0:
            # add child items
            bom = frappe.get_doc("BOM", boms[0]['name'])
            for i in bom.items:
                for expanded_item in check_item(i.item_code, qty * i.qty):
                    stock_items.append(expanded_item)
        else:
            # no BOM, add item
            stock_items.append({'item_code': item_code, 'qty': qty})
    return stock_items

""" This function checks if qty of item_code is available """
def check_availability(item_code, qty):
    sql_query = """SELECT '{item_code}' AS `item_code`,
                     {qty} AS `qty`,
                     IFNULL(SUM(`actual_qty`), 0) AS `actual_qty`,
                     IFNULL(SUM(`projected_qty`), 0) AS `projected_qty`,
                     IF(SUM(`actual_qty`) > {qty}, 1, 0) AS `ok_now`,
                     IF(SUM(`projected_qty`) > {qty}, 1, 0) AS `ok_future`
                   FROM `tabBin`
                   WHERE `item_code` = '{item_code}';""".format(item_code=item_code, qty=qty)
    data = frappe.db.sql(sql_query, as_dict=True)
    return data
