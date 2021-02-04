# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe import _

def execute(filters=None):
    columns, data = [], []

    columns = get_columns()
    data = get_values()
    
    return columns, data

def get_columns():
    return [
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 80},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Delivery date"), "fieldname": "delivery_date", "fieldtype": "Darte", "width": 100},
        {"label": _("KW"), "fieldname": "kw", "fieldtype": "Data", "width": 75},
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 75},
        {"label": _("Auftragsvolumen"), "fieldname": "sales_order_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Verrechnet"), "fieldname": "per_billed", "fieldtype": "Percent", "width": 75},
        {"label": _("Offen"), "fieldname": "open_value", "fieldtype": "Currency", "width": 120},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20},
    ]


def get_values():
    # sales orders
    sql_query = """SELECT 
          `name` AS `sales_order`, 
          `customer` AS `customer`, 
          `customer_name` AS `customer_name`, 
          `transaction_date` AS `date`, 
          `delivery_date` AS `delivery_date`,
          `base_net_total` AS `sales_order_value`,
          SUBSTRING(`delivery_date`, 1, 7) AS `month`,
          CONCAT(YEAR(`delivery_date`), "-", WEEK(`delivery_date`, 1)) AS `kw`,
          `per_billed` AS `per_billed`,
          ((100 - `per_billed`)/100) * `base_net_total` AS `open_value`
        FROM `tabSales Order`
        WHERE `docstatus` = 1 
          AND `status` NOT IN ('Closed', 'Completed')
        ORDER BY `delivery_date` ASC;"""
    sales_orders = frappe.db.sql(sql_query, as_dict=True)

    # aggregate and write intermediate sums
    last_week = None
    week_total = 0
    week_open = 0
    last_month = None
    month_total = 0
    month_open = 0
    data = []
    for so in sales_orders:
        # check if a new week starts
        if last_week and last_week != so['kw']:
            data.append({
                'customer_name': (_("Total KW {0}")).format(last_week), 
                'sales_order_value': week_total,
                'kw': last_week,
                'open_value': week_open,
                'per_billed': 100 * (week_open / (week_total)) if week_total > 0 else 0
            })
            week_total = 0
            week_open = 0
        # check if a new month starts
        if last_month and last_month != so['month']:
            data.append({
                'customer_name': (_("Total {0}")).format(last_month), 
                'sales_order_value': month_total,
                'month': last_month,
                'open_value': month_open,
                'per_billed': 100 * (month_open / (month_total)) if month_total > 0 else 0
            })
            month_total = 0  
            month_open = 0 
        # update weeks
        last_week = so['kw']
        last_month = so['month']
        week_total += so['sales_order_value']
        month_total += so['sales_order_value']
        week_open += so['open_value']
        month_open += so['open_value']
        # insert sales order
        data.append(so)
    # insert final total rows
    data.append({
                'customer_name': (_("Total KW {0}")).format(last_week), 
                'sales_order_value': week_total,
                'kw': last_week,
                'open_value': week_open,
                'per_billed': 100 * (week_open / (week_total)) if week_total > 0 else 0
            })
    data.append({
                'customer_name': (_("Total {0}")).format(last_month), 
                'sales_order_value': month_total,
                'month': last_month,
                'open_value': month_open,
                'per_billed': 100 * (month_open / (month_total)) if month_total > 0 else 0
            })
    
    return data
