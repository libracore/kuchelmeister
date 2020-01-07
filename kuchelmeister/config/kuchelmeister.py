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
                   }
            ]
        }
]
