# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com)
#              Julio (julio@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields


class AccountTax(osv.Model):
    _inherit = "account.tax"

    _columns = {
        'tax_voucher_ok': fields.boolean('Tax Vocuher Ok', help='help'),
        'account_collected_voucher_id': fields.many2one(
            'account.account', 'Account Collected Voucher'),
        'account_paid_voucher_id': fields.many2one(
            'account.account', 'Account Paid Voucher'),
        'account_retention_voucher_id': fields.many2one(
            'account.account', 'VAT pending for apply Account',
            help='VAT pending for apply due to Withholding Tax'),
        'account_expense_voucher_id': fields.many2one(
            'account.account', 'Account Expense Voucher'),
        'account_income_voucher_id': fields.many2one(
            'account.account', 'Account Income Voucher'),
        'tax_diot': fields.selection(
            [('tax_16', 'IVA 16'), ('tax_11', 'IVA 11'),
             ('tax_exe', 'IVA EXENTO'), ('tax0', 'IVA CERO'),
             ('tax_ret', 'IVA RETENIDO')],
            'Tax to affect in DIOT'),
    }


class AccountJournal(osv.Model):
    _inherit = 'account.journal'

    _columns = {
        'special_journal': fields.boolean(
            'Is special Journal?',
            help="Mark this field when the journal is used to make taxes"
                 " in advance payment or partial payment in voucher.\n"
                 "This journal always should be used with amount = 0.0")
    }


class ResCompany(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'tax_provision_customer': fields.many2one(
            'account.tax',
            'Provision tax Customer',
            domain=[('type_tax_use', '=', 'sale')],
            help="Tax to use when create taxes from advance payment "
                 "to Customer"),
        'tax_provision_supplier': fields.many2one(
            'account.tax',
            'Provision tax Supplier',
            domain=[('type_tax_use', '=', 'purchase')],
            help="Tax to use when create taxes from advance payment "
                 "to Supplier")

    }
