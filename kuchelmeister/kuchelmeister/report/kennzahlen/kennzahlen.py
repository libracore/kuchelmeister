# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe import _

def execute(filters=None):
    columns, data = [], []

    columns = get_columns()

    first_date = find_first_kw_start_date(filters.year)

    data = []
    for kw in range(1, 53, 1):
        data.append(get_values_for_kw(kw, first_date, first_date + timedelta(days=6)))
        first_date = first_date + timedelta(days=7)

    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Data", "width": 50},
        {"label": _("Net Revenue [CHF]"), "fieldname": "revenue", "fieldtype": "Currency", "width": 150},
        {"label": _("Fehlermeldungen"), "fieldname": "issues", "fieldtype": "Data", "width": 50}
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
