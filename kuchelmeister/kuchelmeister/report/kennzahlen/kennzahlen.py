# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe import _

def execute(filters=None):
    columns, data = [], []

    columns = get_columns()
    
    if filters.from_date and filters.to_date:
        data = [get_values(filters.from_date, filters.to_date)]
    else:
        data = []
        
    return columns, data

def get_columns():
    return [
        #{"label": _("Date"), "fieldname": "date", "fieldtype": "Data", "width": 50},
        {"label": _("Acquisition"), "fieldname": "customer_visits", "fieldtype": "Int", "width": 120},
        {"label": _("Angebote"), "fieldname": "quotations", "fieldtype": "Int", "width": 75},
        {"label": _("Angebotsvolumen"), "fieldname": "quotation_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Bestellt"), "fieldname": "quotation_success_rate", "fieldtype": "Percent", "width": 70},
        {"label": _("D. Dauer [h]"), "fieldname": "quotation_edit_time", "fieldtype": "Float", "precision": 1, "width": 100},
        {"label": _("Aufträge"), "fieldname": "sales_orders", "fieldtype": "Int", "width": 75},
        {"label": _("Auftragsvolumen"), "fieldname": "sales_order_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Lieferungen"), "fieldname": "delivery_notes", "fieldtype": "Int", "width": 100},
        {"label": _("Liefervolumen"), "fieldname": "delivery_note_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Rechnungen"), "fieldname": "sales_invoices", "fieldtype": "Int", "width": 100},
        {"label": _("Nettoumsatz"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
        {"label": _("Fehlermeldungen"), "fieldname": "issues", "fieldtype": "Data", "width": 120},
        {"label": _("Fehlerzeit [h]"), "fieldname": "issue_hours", "fieldtype": "Float", "precision": 1, "width": 100},
        {"label": _("Fehlerkosten"), "fieldname": "issue_costs", "fieldtype": "Currency", "width": 100},
        {"label": _("Sollzeit [h]"), "fieldname": "soll_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Istzeit [h]"), "fieldname": "ist_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Ferien [h]"), "fieldname": "ferien_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Krankheit [h]"), "fieldname": "krank_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Wirtschaftlichkeit"), "fieldname": "profitability", "fieldtype": "Currency", "width": 120}
    ]


def get_values(from_date, to_date):
    # quotation KPIs
    sql_query = """SELECT
       IFNULL(SUM(`tabQuotation`.`potential`), 0) AS `revenue`,
       IFNULL(COUNT(`tabQuotation`.`base_net_total`), 0) AS `count`,
       (SELECT IFNULL(COUNT(`tQ1`.`name`), 0) 
        FROM `tabQuotation` AS `tQ1`
        WHERE `tQ1`.`docstatus` = 1
        AND `tQ1`.`transaction_date` >= '{from_date}'
        AND `tQ1`.`transaction_date` <= '{to_date}'
        AND `tQ1`.`status` = "Ordered") AS `ordered_count`,
       IFNULL(AVG(TIMESTAMPDIFF(HOUR, `tabQuotation`.`creation`, `tabQuotation`.`modified`)), 0) AS `hours`
     FROM `tabQuotation`
     WHERE
       tabQuotation.`docstatus` = 1
       AND `tabQuotation`.`transaction_date` >= '{from_date}'
       AND `tabQuotation`.`transaction_date` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    qtn_info = frappe.db.sql(sql_query, as_dict=True)[0]

    # sales order KPIs
    sql_query = """SELECT
       IFNULL(SUM(`tabSales Order`.`base_net_total`), 0) AS `revenue`,
       IFNULL(COUNT(`tabSales Order`.`base_net_total`), 0) AS `count`
     FROM `tabSales Order`
     WHERE
       `tabSales Order`.`docstatus` = 1
       AND `tabSales Order`.`transaction_date` >= '{from_date}'
       AND `tabSales Order`.`transaction_date` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    order_info = frappe.db.sql(sql_query, as_dict=True)[0]
        
    # delivery KPIs
    sql_query = """SELECT
       IFNULL(SUM(`tabDelivery Note`.`base_net_total`), 0) AS `revenue`,
       IFNULL(COUNT(`tabDelivery Note`.`base_net_total`), 0) AS `count`
     FROM `tabDelivery Note`
     WHERE
       `tabDelivery Note`.`docstatus` = 1
       AND `tabDelivery Note`.`posting_date` >= '{from_date}'
       AND `tabDelivery Note`.`posting_date` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    delivery_info = frappe.db.sql(sql_query, as_dict=True)[0]
            
    # revenue (sales invoice) KPIs
    sql_query = """SELECT
       IFNULL(SUM(`tabSales Invoice`.`base_net_total`), 0) AS `revenue`,
       IFNULL(COUNT(`tabSales Invoice`.`base_net_total`), 0) AS `count`
     FROM `tabSales Invoice`
     WHERE
       `tabSales Invoice`.`docstatus` = 1
       AND `tabSales Invoice`.`posting_date` >= '{from_date}'
       AND `tabSales Invoice`.`posting_date` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    sales_info = frappe.db.sql(sql_query, as_dict=True)[0]
    
    # issue KPIs
    sql_query = """SELECT
       IFNULL(COUNT(`tabNon Conformity Report 8D`.`name`), 0) AS `count`,
       IFNULL(SUM(`tabNon Conformity Report 8D`.`total_kosten`), 0) AS `costs`,
       IFNULL(SUM(`tabNon Conformity Report 8D`.`total_aufwand`), 0) AS `hours`
     FROM `tabNon Conformity Report 8D`
     WHERE
       `tabNon Conformity Report 8D`.`creation` >= '{from_date}'
       AND `tabNon Conformity Report 8D`.`creation` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    issue_info = frappe.db.sql(sql_query, as_dict=True)[0]

    # customer KPIs
    sql_query = """SELECT
       IFNULL(COUNT(`tabKundenbesuch`.`name`), 0) AS `count`
     FROM `tabKundenbesuch`
     WHERE
       `tabKundenbesuch`.`creation` >= '{from_date}'
       AND `tabKundenbesuch`.`creation` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    customer_info = frappe.db.sql(sql_query, as_dict=True)[0]

    # time KPIs
    sql_query = """SELECT
       IFNULL(SUM(`tabStundenerfassung`.`soll_stunden`), 0) AS `soll_stunden`,
       IFNULL(SUM(`tabStundenerfassung`.`ist_stunden`), 0) AS `ist_stunden`,
       IFNULL(SUM(`tabStundenerfassung`.`krank_stunden`), 0) AS `krank_stunden`,
       IFNULL(SUM(`tabStundenerfassung`.`ferien_stunden`), 0) AS `ferien_stunden`
     FROM `tabStundenerfassung`
     WHERE
       `tabStundenerfassung`.`von_datum` >= '{from_date}'
       AND `tabStundenerfassung`.`von_datum` <= '{to_date}'""".format(from_date=from_date, to_date=to_date)
    time_info = frappe.db.sql(sql_query, as_dict=True)[0]
            
    if qtn_info['ordered_count'] > 0:
        qtn_success = 100 * qtn_info['ordered_count'] / qtn_info['count']
    else:
        qtn_success = 0
    if time_info['ist_stunden'] > 0:
        profitability = sales_info['revenue'] / time_info['ist_stunden']
    else:
        profitability = 0
    data = {
        'quotations': qtn_info['count'],
        'quotation_value': qtn_info['revenue'],
        'quotation_success_rate': qtn_success,
        'quotation_edit_time': qtn_info['hours'],
        'sales_orders': order_info['count'],
        'sales_order_value': order_info['revenue'],
        'delivery_notes': delivery_info['count'],
        'delivery_note_value': delivery_info['revenue'],
        'sales_invoices': sales_info['count'],
        'revenue': sales_info['revenue'],
        'issues': issue_info['count'],
        'issue_costs': issue_info['costs'],
        'issue_hours': issue_info['hours'],
        'customer_visits': customer_info['count'],
        'soll_stunden': time_info['soll_stunden'],
        'ist_stunden': time_info['ist_stunden'],
        'krank_stunden': time_info['krank_stunden'],
        'ferien_stunden': time_info['ferien_stunden'],
        'profitability': profitability
    }
    
    
    return data
