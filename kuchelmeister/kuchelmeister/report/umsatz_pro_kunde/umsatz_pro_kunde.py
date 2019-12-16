# Copyright (c) 2016-2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
    columns, data = [], []
    
    columns = ["Customer:Link/Customer:100", 
        "Customer Name:Data:200", 
        "Net Revenue:Currency:150"
    ]
    
    if not filters.from_date:
        filters.from_date = "2000-01-01"
    if not filters.end_date:
        filters.end_date = "2999-12-31"
        
    data = frappe.db.sql("""SELECT
            `customer` AS \"Customer:Link/Customer:100\",
            `customer_name` AS \"Customer Name:Data:200\",
            SUM(`base_net_total`) AS \"Net Revenue:Currency:150\"
        FROM `tabSales Invoice`
        WHERE
            `docstatus` = 1 
            AND `posting_date` >= \"{start_date}\"
            AND `posting_date` <= \"{end_date}\"
            AND IFNULL(`base_net_total`, 0) > 0 
        GROUP BY
            `customer`
        ORDER BY
            \"Net Revenue:Currency:150\"""".format(
            start_date=filters.from_date, end_date=filters.end_date), as_list = True)

    return columns, data
