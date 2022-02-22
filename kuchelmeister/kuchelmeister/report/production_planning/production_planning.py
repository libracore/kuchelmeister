# Copyright (c) 2019-2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast      # to parse str to dict (from JS calls)

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_planning_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 140},
        {"label": _("Bestand"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Bedarf Kundenauftr."), "fieldname": "reserved_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Bedarf Arbeitsauftr."), "fieldname": "reserved_qty_for_production", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Bestellt"), "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("In Fertigung"), "fieldname": "indented_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Erwartet"), "fieldname": "projected_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Sicherheitsbestand"), "fieldname": "safety_stock", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Erwartet inkl. Sicherheit"), "fieldname": "projected_safety_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _(""), "fieldname": "blank", "width": 20}
    ]

@frappe.whitelist()
def get_planning_data(filters, only_reorder=0):
    conditions = []
    if int(only_reorder) == 1:
        conditions.append("(`tabBin`.`projected_qty` - `tabItem`.`safety_stock`) < 0")
    if type(filters) is str:
        filters = ast.literal_eval(filters)
        try:
            if filters['warehouse']:
                conditions.append("`tabBin`.`warehouse` = '{0}'".format(filters['warehouse']))
            if filters['only_reorder']:
                conditions.append("(`tabBin`.`projected_qty` - `tabItem`.`safety_stock`) < 0")
            if filters['has_safety_stock'] == 1:
                conditions.append("(`tabItem`.`safety_stock` > 0)")
            if filters['hide_no_transactions'] == 1:
                conditions.append("(`tabBin`.`actual_qty` > 0 OR `tabBin`.`reserved_qty` > 0 OR `tabBin`.`ordered_qty` > 0 OR `tabBin`.`projected_qty` > 0)")
            if filters['item_group']:
                conditions.append("`tabItem`.`item_group` = '{0}'".format(filters['item_group']))
        except:
            pass
    else:
        if filters.warehouse:
            conditions.append("`tabBin`.`warehouse` = '{0}'".format(filters.warehouse))
        if filters.only_reorder:
            conditions.append("(`tabBin`.`projected_qty` - `tabItem`.`safety_stock`) < 0")
        if filters.has_safety_stock == 1:
            conditions.append("(`tabItem`.`safety_stock` > 0)")
        if filters.hide_no_transactions == 1:
            conditions.append("(`tabBin`.`actual_qty` > 0 OR `tabBin`.`reserved_qty` > 0 OR `tabBin`.`ordered_qty` > 0 OR `tabBin`.`projected_qty` > 0)")
        if filters.item_group:
            conditions.append("`tabItem`.`item_group` = '{0}'".format(filters.item_group))
                
    sql_query = """SELECT
        `tabBin`.`item_code` AS `item_code`, 
        `tabItem`.`item_name` AS `item_name`, 
        `tabItem`.`item_group` AS `item_group`,
        `tabBin`.`warehouse` AS `warehouse`, 
        `tabBin`.`actual_qty` AS `actual_qty`, 
        `tabBin`.`reserved_qty` AS `reserved_qty`,
        `tabBin`.`reserved_qty_for_production` AS `reserved_qty_for_production`,
        `tabBin`.`ordered_qty` AS `ordered_qty`,
        `tabBin`.`indented_qty` AS `indented_qty`,
        `tabBin`.`projected_qty` AS `projected_qty`,
        `tabItem`.`safety_stock` AS `safety_stock`,
        (`tabBin`.`projected_qty` - `tabItem`.`safety_stock`) AS `projected_safety_qty`
      FROM `tabBin`
      LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBin`.`item_code`
      LEFT JOIN `tabItem Default` ON 
        (`tabItem Default`.`parenttype` = 'Item' AND `tabItem Default`.`parent` = `tabBin`.`item_code`)
      {conditions} 
      ORDER BY `tabBin`.`projected_qty` ASC
      """.format(conditions=" WHERE " + " AND ".join(conditions) if conditions else "")

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
