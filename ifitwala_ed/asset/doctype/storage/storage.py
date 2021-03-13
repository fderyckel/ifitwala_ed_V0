# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ifitwala_ed.asset import get_storage_account
from frappe.utils import cint, nowdate
from frappe import _
from frappe.utils.nestedset import NestedSet

class Storage(NestedSet):
	nsm_parent_field = 'parent_storage'

	def autoname(self):
		if self.school:
			suffix = " - " + frappe.get_cached_value("School", self.school, "abbr")
			if not self.storage_name.endswith(suffix):
				self.name = self.storage_name + suffix
		else:
			self.name = self.storage_name

	def onload(self):
		'''load account name for General Ledger Report'''
		if self.school and cint(frappe.db.get_value("School", self.school, "enable_perpetual_inventory")):
			account = self.account or get_storage_account(self)
			if account:
				self.set_onload('account', account)

	def on_update(self):
		self.update_nsm_model()

	def before_rename(self, old_name, new_name, merge=False):
		super(Storage, self).before_rename(old_name, new_name, merge)

		# Add school abbr if not provided
		new_storage = ifitwala_ed.encode_school_abbr(new_name, self.school)

		if merge:
			if not frappe.db.exists("Storage", new_storage):
				frappe.throw(_("Storage {0} does not exist").format(new_storage))

			if self.school != frappe.db.get_value("Storage", new_storage, "school"):
				frappe.throw(_("Both Storage must belong to same School."))

		return new_storage

	def after_rename(self, old_name, new_name, merge=False):
		super(Storage, self).after_rename(old_name, new_name, merge)

		new_storage_name = self.get_new_storage_name_without_abbr(new_name)
		self.db_set("storage_name", new_storage_name)

		if merge:
			self.recalculate_bin_qty(new_name)

	def on_trash(self):
		bins = frappe.db.sql("""SELECT * FROM `tabBin` WHERE storage = %s""", self.name, as_dict=1)
		for bin in bins:
			if bin["actual_qty"] or bin["ordered_qty"] or bin ["requested_qty"]:
				frappe.throw(_("Storage {0} cannot be deleted as quantity exist for Item {1}.").format(self.name, bin['item_code']))

		if self.check_if_sle_exists():
			throw(_("Storage can not be deleted as stock ledger entry exists for this storage."))
		if self.check_if_child_exists():
			throw(_("Child storage exists for this storage. You can not delete this storage."))

		self.update_nsm_model()

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	def check_if_sle_exists(self):
		return frappe.db.sql("""SELECT name FROM `tabStock Ledger Entry` WHERE storage = %s limit 1""", self.name)

	def check_if_child_exists(self):
		return frappe.db.sql("""SELECT name FROM `tabStorage` WHERE parent_storage = %s limit 1""", self.name)

	def get_new_storage_name_without_abbr(self, name):
		school_abbr = frappe.get_cached_value("School",  self.school,  "abbr")
		parts = name.rsplit(" - ", 1)

		if parts[-1].lower() == school_abbr.lower():
			name = parts[0]

		return name

	def recalculate_bin_qty(self, new_name):
		from ifitwala_ed.asset.stock_balance import repost_stock
		frappe.db.auto_commit_on_many_writes = 1
		existing_allow_negative_stock = frappe.db.get_value("Stock Settings", None, "allow_negative_stock")
		frappe.db.set_value("Stock Settings", None, "allow_negative_stock", 1)

		repost_stock_for_items = frappe.db.sql_list("""SELECT DISTINCT item_code FROM `tabBin` WHERE storage = %s""", new_name)

		# Delete all existing bins to avoid duplicate bins for the same item and storage
		frappe.db.sql("delete from `tabBin` where storage = %s", new_name)

		for item_code in repost_stock_for_items:
			repost_stock(item_code, new_name)

		frappe.db.set_value("Stock Settings", None, "allow_negative_stock", existing_allow_negative_stock)
		frappe.db.auto_commit_on_many_writes = 0

	def convert_to_group_or_ledger(self):
		if self.is_group:
			self.convert_to_ledger()
		else:
			self.convert_to_group()

	def convert_to_ledger(self):
		if self.check_if_child_exists():
			frappe.throw(_("Storage with child nodes cannot be converted to ledger"))
		elif self.check_if_sle_exists():
			throw(_("Storage with existing transaction can not be converted to ledger."))
		else:
			self.is_group = 0
			self.save()
			return 1

	def convert_to_group(self):
		if self.check_if_sle_exists():
			throw(_("Storage with existing transaction can not be converted to group."))
		else:
			self.is_group = 1
			self.save()
			return 1


@frappe.whitelist()
def get_children(doctype, parent=None, school=None, is_root=False):
	from ifitwala_ed.asset.utils import get_stock_value_from_bin

	if is_root:
		parent = ""

	fields = ['name as value', 'is_group as expandable']
	filters = [
		['docstatus', '<', '2'],
		['ifnull(`parent_storage`, "")', '=', parent],
		['school', 'in', (school, None,'')]
	]

	storages = frappe.get_list(doctype, fields=fields, filters=filters, order_by='name')

	# return warehouses
	for sto in storages:
		sto["balance"] = get_stock_value_from_bin(storage=sto.value)
		if school:
			sto["school_currency"] = frappe.db.get_value("School", school, 'default_currency')
	return storages

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = make_tree_args(**frappe.form_dict)

	if cint(args.is_root):
		args.parent_storage = None

	frappe.get_doc(args).insert()
