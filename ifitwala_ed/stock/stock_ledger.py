# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
import copy
from frappe import _
from frappe.utils import cint, flt, cstr, now, get_link_to_form
from frappe.model.meta import get_field_precision
import json
from six import iteritems

# future reposting
class NegativeStockError(frappe.ValidationError): pass
class SerialNoExistsInFutureTransaction(frappe.ValidationError): pass


_exceptions = frappe.local('stockledger_exceptions')
# _exceptions = []

def make_sl_entries(sl_entries, allow_negative_stock=False, via_landed_cost_voucher=False):
	from ifitwala_ed.controllers.stock_controller import future_sle_exists
	if sl_entries:
		from ifitwala_ed.stock.utils import update_bin

		cancel = sl_entries[0].get("is_cancelled")
		if cancel:
			validate_cancellation(sl_entries)
			set_as_cancel(sl_entries[0].get('voucher_type'), sl_entries[0].get('voucher_no'))

		args = get_args_for_future_sle(sl_entries[0])
		future_sle_exists(args, sl_entries)




def validate_cancellation(args):
	if args[0].get("is_cancelled"):
		repost_entry = frappe.db.get_value("Repost Item Valuation", {
			'voucher_type': args[0].voucher_type,
			'voucher_no': args[0].voucher_no,
			'docstatus': 1
		}, ['name', 'status'], as_dict=1)

		if repost_entry:
			if repost_entry.status == 'In Progress':
				frappe.throw(_("Cannot cancel the transaction. Reposting of item valuation on submission is not completed yet."))
			if repost_entry.status == 'Queued':
				doc = frappe.get_doc("Repost Item Valuation", repost_entry.name)
				doc.cancel()
				doc.delete()

def set_as_cancel(voucher_type, voucher_no):
	frappe.db.sql("""update `tabStock Ledger Entry` set is_cancelled=1,
		modified=%s, modified_by=%s
		where voucher_type=%s and voucher_no=%s and is_cancelled = 0""",
		(now(), frappe.session.user, voucher_type, voucher_no))

def get_args_for_future_sle(row):
	return frappe._dict({
		'voucher_type': row.get('voucher_type'),
		'voucher_no': row.get('voucher_no'),
		'posting_date': row.get('posting_date'),
		'posting_time': row.get('posting_time')
	})

def validate_serial_no(sle):
	from ifitwala_ed.stock.doctype.serial_no.serial_no import get_serial_nos
	for sn in get_serial_nos(sle.serial_no):
		args = copy.deepcopy(sle)
		args.serial_no = sn
		args.warehouse = ''

		vouchers = []
		for row in get_stock_ledger_entries(args, '>'):
			voucher_type = frappe.bold(row.voucher_type)
			voucher_no = frappe.bold(get_link_to_form(row.voucher_type, row.voucher_no))
			vouchers.append(f'{voucher_type} {voucher_no}')

		if vouchers:
			serial_no = frappe.bold(sn)
			msg = (f'''The serial no {serial_no} has been used in the future transactions so you need to cancel them first.
				The list of the transactions are as below.''' + '<br><br><ul><li>')

			msg += '</li><li>'.join(vouchers)
			msg += '</li></ul>'

			title = 'Cannot Submit' if not sle.get('is_cancelled') else 'Cannot Cancel'
			frappe.throw(_(msg), title=_(title), exc=SerialNoExistsInFutureTransaction)
