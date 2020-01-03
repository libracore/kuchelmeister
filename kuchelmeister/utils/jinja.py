# Copyright (c) 2016-2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def expand_so_bom(sales_order):
    so = frappe.get_doc("Sales Order", sales_order)
    expanded_positions = []
    for item in so.items:
        details = expand_item(item.item_code, item.qty, 0)
        for detail in details:
            expanded_positions.append(detail)
    return expanded_positions
    
def expand_item(item_code, qty, level):
    positions = [{'item_code': item_code, 'qty': qty, 'level': level}]
    # find bom
    active_boms = frappe.get_all("BOM", 
        filters={'item': item_code, 'docstatus': 1, 'is_active': 1, 'is_default': 1},
        fields=['name'])
    if active_boms and len(active_boms) > 0:
        bom = frappe.get_doc("BOM", active_boms[0]['name'])
        for item in bom.items:
            children = expand_item(item.item_code, item.qty * qty, (level + 1))
            for child in children:
                positions.append(child)
    return positions

@frappe.whitelist()
def get_so_materials(sales_order):
    materials = []
    all_items = expand_so_bom(sales_order)
    for item in all_items:
        material = frappe.get_value("Item", item['item_code'], "material")
        if material and material not in materials:
            materials.append(material)
    return materials
