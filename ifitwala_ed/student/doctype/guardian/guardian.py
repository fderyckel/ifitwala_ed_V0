# -*- coding: utf-8 -*-
# Copyright (c) 2020, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.csvutils import getlink
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact

class Guardian(Document):

    def __setup__(self):
            self.onload()

    ## to load students for quick view
    def onload(self):
            load_address_and_contact(self)
            self.load_students()

    ## to load studens from the database
    def load_students(self):
            self.students = []
            ## Basically, we load the students name based on the gstudent guardian child table.
            students = frappe.get_all("Student Guardian", filters = {"guardian":self.name}, fields = ["parent"])
            for student in students:
                    self.append("students", {
                            "student":student.parent,
                            "student_name":frappe.db.get_value("Student", student.parent, "student_full_name"),
                            "student_gender": frappe.db.get_value("Student", student.parent, "student_gender")
                    })

    def before_insert(self):
        self.contact_doc = self.create_address()

    def validate(self):
        self.guardian_full_name = self.guardian_first_name + " " + self.guardian_last_name
        self.students = []

    def after_insert(self):
        self.update_links()

    def create_contact(self):
        contact = frappe.get_doc("Contact")
        contact.update({
            "first_name": self.guardian_first_name,
            "last_name": self.guardian_last_name,
        })
        if self.salutation:
            contact.append("salutation": self.salutation)
        if self.guardian_gender:
            contact.append("gender": self.guardian_gender)
        if self.guardian_email:
            contact.append("email_ids", {"email_id": self.guardian_email, "is_primary": 1})
        if self.guardian_mobile_phone:
            contact.append("phone_nos", {"phone": self.guardian_mobile_phone})
        contact.insert(ignore_permissions=True)

        return contact

    def update_links(self):
        if self.contact_doc:
            self.contact_doc.append("links", {
                "link_doctype": "Guardian",
                "link_name": self.name,
                "link_title": self.guardian_full_name
            })
            self.contact_doc.save()



# to support the invite_guardian method on the JS side.
@frappe.whitelist()
def invite_guardian(guardian):
    guardian_doc = frappe.get_doc("Guardian", guardian)
    if not guardian_doc.guardian_email:
        frappe.throw(_("Please add an email address and try again."))
    else:
        guardian_as_user = frappe.get_value('User', dict(email = guardian_doc.guardian_email))
        if guardian_as_user:
            # Using msgprint as we do not want to throw an exception.  Just informing the user already exist in the db.
            frappe.msgprint(_("The user {0} already exists.").format(getlink("User", guardian_as_user)))
        else:
            user = frappe.get_doc({
                "doctype": "User",
                "first_name": guardian_doc.guardian_first_name,
                "last_name": guardian_doc.guardian_last_name,
                "email": guardian_doc.guardian_email,
                "mobile_no": guardian_doc.guardian_mobile_phone,
                "user_type": "Website User",
                "send_welcome_email": 1
            })
            user.flags.ignore_permissions = True
            user.add_roles("Guardian")
            user.save(ignore_permissions = True)
            update_password_link = user.reset_password()
            frappe.msgprint(_("User {0} created and welcomed with an email").format(getlink("User", user.name)))
            return user.name
