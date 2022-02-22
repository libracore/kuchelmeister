# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class TrumpfSettings(Document):
    def validate(self):
        # make sure path is unix-type
        self.physical_path = self.physical_path.replace("\\", "/")
        self.archive_path = self.archive_path.replace("\\", "/")
        # make sure path is ending with a dash
        if not self.physical_path.endswith("/"):
            self.physical_path += "/"
            # make sure path is unix-type
        if not self.archive_path.endswith("/"):
            self.archive_path += "/"        

        return
