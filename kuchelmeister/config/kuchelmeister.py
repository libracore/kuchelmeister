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
        }
]
