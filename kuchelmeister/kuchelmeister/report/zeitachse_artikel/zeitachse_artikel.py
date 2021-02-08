# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast      # to parse str to dict (from JS calls)

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 140},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 100},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Type"), "fieldname": "type", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = []
    if filters.item_code:
        item_code = filters.item_code
    else:
        return []
                    
    sql_query = """SELECT * FROM 
  (SELECT 
    `tabSales Order Item`.`delivery_date` AS `date`,
    ((-1) * `tabSales Order Item`.`qty`) AS `qty`,
    `tabSales Order`.`name` AS `sales_order`,
    "" AS `work_order`,
    "Endprodukt" AS `type`
  FROM `tabSales Order Item`
  LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
  WHERE `tabSales Order Item`.`item_code` = '{item_code}'
     AND `tabSales Order`.`docstatus` = 1
     AND `tabSales Order`.`status` IN ("To Deliver", "To Deliver and Bill")
  UNION SELECT 
    `tabWork Order`.`planned_start_date` AS `date`,
    ((-1) * `tabWork Order Item`.`required_qty`) AS `qty`,
    `tabWork Order`.`sales_order` AS `sales_order`,
    `tabWork Order`.`name` AS `work_order`,
    "Vorstufe" AS `type`
   FROM `tabWork Order Item`
   LEFT JOIN `tabWork Order` ON `tabWork Order`.`name` = `tabWork Order Item`.`parent`
   WHERE `tabWork Order Item`.`item_code` = '{item_code}'
     AND `tabWork Order`.`docstatus` = 1
     AND `tabWork Order`.`status` IN ("Not Started")
  UNION SELECT 
    `tabWork Order`.`expected_delivery_date` AS `date`,
    `tabWork Order`.`qty` AS `qty`,
    `tabWork Order`.`sales_order` AS `sales_order`,
    `tabWork Order`.`name` AS `work_order`,
    "Endprodukt" AS `type`
   FROM `tabWork Order`
   WHERE `tabWork Order`.`production_item` = '{item_code}'
     AND `tabWork Order`.`docstatus` = 1
     AND `tabWork Order`.`status` IN ("Not Started")
  ) AS `timeline`
  ORDER BY `timeline`.`date` ASC;
      """.format(item_code=item_code)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
