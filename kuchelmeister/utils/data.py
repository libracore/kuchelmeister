# Copyright (c) 2016-2019, libracore and contributors
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
