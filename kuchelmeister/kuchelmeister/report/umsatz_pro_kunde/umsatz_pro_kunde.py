# Copyright (c) 2016-2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    columns = get_columns()
    
    if not filters.from_date:
        filters.from_date = "2000-01-01"
    if not filters.end_date:
        filters.end_date = "2999-12-31"
        
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": _("Kunde"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Kundenname"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": _("Nettoumsatz"), "fieldname": "net_revenue", "fieldtype": "Currency", "width": 150},
        {"label": _("Offerten"), "fieldname": "quotations", "fieldtype": "Int", "width": 75},
        {"label": _("Offertenvolumen"), "fieldname": "quotation_volume", "fieldtype": "Currency", "width": 100},
        {"label": _("Bestellte Offerten"), "fieldname": "ordered", "fieldtype": "Percentage", "width": 75},
        {"label": _("Aufträge"), "fieldname": "sales_orders", "fieldtype": "Int", "width": 75},
        {"label": _(""), "fieldname": "", "fieldtype": "Data", "width": 20}
    ]
    
def get_data(filters):
    sql_query = """
        SELECT *, CONCAT(ROUND((100 * `raw`.`quotations_ordered` / `raw`.`quotations`), 0), "%") AS `ordered`
        FROM (SELECT
            `tabCustomer`.`name` AS 'customer',
            `tabCustomer`.`customer_name` AS 'customer_name',
            (SELECT SUM(`tSI1`.`base_net_total`)
             FROM `tabSales Invoice` AS `tSI1`
             WHERE `tSI1`.`customer` = `tabCustomer`.`name`
               AND `tSI1`.`docstatus` = 1
               AND `tSI1`.`posting_date` >= '{start_date}'
               AND `tSI1`.`posting_date` <= '{end_date}') AS `net_revenue`,
            (SELECT COUNT(`tQtn1`.`name`)
             FROM `tabQuotation` AS `tQtn1`
             WHERE `tQtn1`.`party_name` = `tabCustomer`.`name`
               AND `tQtn1`.`docstatus` = 1
               AND `tQtn1`.`transaction_date` >= '{start_date}'
               AND `tQtn1`.`transaction_date` <= '{end_date}') AS `quotations`,
            (SELECT SUM(`tQtn2`.`base_net_total`)
             FROM `tabQuotation` AS `tQtn2`
             WHERE `tQtn2`.`party_name` = `tabCustomer`.`name`
               AND `tQtn2`.`docstatus` = 1
               AND `tQtn2`.`transaction_date` >= '{start_date}'
               AND `tQtn2`.`transaction_date` <= '{end_date}') AS `quotation_volume`,
            (SELECT COUNT(`tQtn3`.`name`)
             FROM `tabQuotation` AS `tQtn3`
             WHERE `tQtn3`.`party_name` = `tabCustomer`.`name`
               AND `tQtn3`.`docstatus` = 1
               AND `tQtn3`.`status` = "Ordered"
               AND `tQtn3`.`transaction_date` >= '{start_date}'
               AND `tQtn3`.`transaction_date` <= '{end_date}') AS `quotations_ordered`,      
            (SELECT COUNT(`tSO1`.`name`)
             FROM `tabSales Order` AS `tSO1`
             WHERE `tSO1`.`customer` = `tabCustomer`.`name`
               AND `tSO1`.`docstatus` = 1
               AND `tSO1`.`transaction_date` >= '{start_date}'
               AND `tSO1`.`transaction_date` <= '{end_date}') AS `sales_orders`  
          FROM `tabCustomer`
          WHERE `tabCustomer`.`disabled` = 0) AS `raw`
        WHERE IFNULL(`raw`.`net_revenue`, 0) > 0 
        ORDER BY `raw`.`net_revenue` DESC;""".format(
            start_date=filters.from_date, end_date=filters.end_date)
    data = frappe.db.sql(sql_query, as_dict = True)
    return data
