# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe import _
from kuchelmeister.kuchelmeister.report.kennzahlen.kennzahlen import get_values
import calendar

def execute(filters=None):
    columns, data = [], []

    columns = get_columns()

    data = []
    for month in range(1, 13, 1):
        first, last = calendar.monthrange(filters.year, month)
        _data = get_values("{y:04d}-{m:02d}-{d:02d}".format(y=filters.year, m=month, d=first), 
                           "{y:04d}-{m:02d}-{d:02d}".format(y=filters.year, m=month, d=last))
        _data['month'] = "{0}".format(month)
        data.append(_data)

    return columns, data

def get_columns():
    return [
        {"label": _("Monat"), "fieldname": "month", "fieldtype": "Int", "width": 50},
        {"label": _("Kundenbesuche"), "fieldname": "customer_visits", "fieldtype": "Int", "width": 120},
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
        {"label": _("Weiterbildung [h]"), "fieldname": "wb_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Militär [h]"), "fieldname": "mil_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Kurzarbeit [h]"), "fieldname": "kz_stunden", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": _("Wirtschaftlichkeit"), "fieldname": "profitability", "fieldtype": "Currency", "width": 120}
    ]

def find_first_kw_start_date(year):
    sql_query="""SELECT DATE_ADD("{year}-01-01", INTERVAL (-WEEKDAY("{year}-01-01")) DAY) AS `date`;""".format(year=year)
    start_date = frappe.db.sql(sql_query, as_dict=True)[0]['date']
    return datetime.strptime(start_date, '%Y-%m-%d')

def get_values_for_kw(kw, start_date, end_date):
    sql_query = """SELECT
       'KW {kw}' AS `date`,
       SUM(`tabSales Invoice`.`base_net_total`) AS `revenue`
     FROM `tabSales Invoice`
     WHERE
       `tabSales Invoice`.`posting_date` >= '{start_date}'
       AND `tabSales Invoice`.`posting_date` <= '{end_date}'""".format(kw=kw, start_date=start_date, end_date=end_date)

    data = frappe.db.sql(sql_query, as_dict=True)

    return data[0]
