# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


def update_profile_from_contact(doc, method = None):
    """update the main doctype if changes made on Contact DocType. Called by hook.py """
    links = doc.get("links")
    phone = doc.get("phone_nos")
    guardian=None
    employee=None
    primary_mobile=None
    for l in links:
        if l.get("link_doctype") == "Guardian":
            guardian = l.get("link_name")
        if l.get("link_doctype") == "Employee":
            employee = l.get("link_name")
    for p in phone:
        if p.get("is_primary_mobile_no") == 1:
            primary_mobile = p.get("phone")
    if guardian:
        guardian_doc = frappe.get_doc("Guardian", guardian)
        guardian_doc.salutation = doc.get("salutation")
        guardian_doc.guardian_gender = doc.get("gender")
        guardian_doc.guardian_mobile_phone = primary_mobile
        guardian_doc.save()
