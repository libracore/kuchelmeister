from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Trumpf"),
            "icon": "octicon oction-code",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Trumpf Settings",
                       "label": _("Trumpf Settings"),
                       "description": _("Trumpf Settings")
                   }
            ]
        },
        {
            "label": _("Documents"),
            "icon": "octicon oction-book",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Anmeldung Subakkordant",
                       "label": _("Anmeldung Subakkordant"),
                       "description": _("Anmeldung Subakkordant")
                   },
                   {
                       "type": "doctype",
                       "name": "Kundenbesuch",
                       "label": _("Kundenbesuch"),
                       "description": _("Kundenbesuch")
                   },
                   {
                       "type": "doctype",
                       "name": "Stundenerfassung",
                       "label": _("Stundenerfassung"),
                       "description": _("Stundenerfassung")
                   }
            ]
        },
        {
            "label": _("Reports"),
            "icon": "octicon oction-book",
            "items": [
                {
					"type": "report",
					"name": "Production Planning",
					"doctype": "Bin",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Zeitachse Artikel",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Umsatz pro Kunde",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Lagerprojektion",
					"doctype": "Bin",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Kennzahlen",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Kennzahlen pro KW",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Kennzahlen pro Monat",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
            ]
        },
        {
            "label": _("Lists"),
            "icon": "octicon oction-book",
            "items": [
                {
					"type": "report",
					"name": "Mahnliste",
					"doctype": "Payment Reminder",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Kontrolle MwSt",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Offertenliste",
					"doctype": "Quotation",
					"is_query_report": True
				},
                {
					"type": "report",
					"name": "Kunden-KPI",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
            ]
        },
        {
            "label": _("Accounting"),
            "icon": "octicon oction-book",
            "items": [
                {
                       "type": "page",
                       "name": "bank_wizard",
                       "label": _("Bank Wizard"),
                       "description": _("Bank Wizard")
                },
                {
                       "type": "doctype",
                       "name": "Payment Proposal",
                       "label": _("Payment Proposal"),
                       "description": _("Payment Proposal")
                },
                {
                       "type": "doctype",
                       "name": "Payment Reminder",
                       "label": _("Payment Reminder"),
                       "description": _("Payment Reminder")
                },
                {
                       "type": "doctype",
                       "name": "Payment Entry",
                       "label": _("Payment Entry"),
                       "description": _("Payment Entry")
                },
				{
					"type": "report",
					"name": "Accounts Receivable",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Accounts Receivable Summary",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Accounts Payable",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Accounts Payable Summary",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				}
            ]
        },
        {
            "label": _("Quality"),
            "icon": "octicon oction-book",
            "items": [
                {
                       "type": "doctype",
                       "name": "Non Conformity Report 8D",
                       "label": _("Non Conformity Report 8D"),
                       "description": _("Non Conformity Report 8D")
                },
                {
                       "type": "doctype",
                       "name": "Inspection Equipment",
                       "label": _("Inspection Equipment"),
                       "description": _("Inspection Equipment")
                }
            ]
        }
]
