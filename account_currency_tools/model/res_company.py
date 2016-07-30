# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp.osv import fields, osv


class ResCompany(osv.Model):
    _inherit = "res.company"
    _description = 'Companies'

    _columns = {  # pylint: disable=W8105
        'bank_gain_exchange_account_id': fields.many2one(
            'account.account', 'Bank Gain Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Bank Gain Exchange Rate Account for booking '
                  'Difference')),
        'rec_gain_exchange_account_id': fields.many2one(
            'account.account', 'Receivable Gain Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Receivable Gain Exchange Rate Account for booking '
                  'Difference')),
        'pay_gain_exchange_account_id': fields.many2one(
            'account.account', 'Payable Gain Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Payable Gain Exchange Rate Account for booking '
                  'Difference')),
        'bank_loss_exchange_account_id': fields.many2one(
            'account.account', 'Bank Loss Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Bank Loss Exchange Rate Account for booking '
                  'Difference')),
        'rec_loss_exchange_account_id': fields.many2one(
            'account.account', 'Receivable Loss Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Receivable Loss Exchange Rate Account for booking '
                  'Difference')),
        'pay_loss_exchange_account_id': fields.many2one(
            'account.account', 'Payable Loss Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Payable Loss Exchange Rate Account for booking '
                  'Difference')),
        'journal_id': fields.many2one(
            'account.journal', 'Posting Journal',
            domain=("[('type','=','general')]"),
            required=False),
        'check_non_multicurrency_account': fields.boolean(
            'Check Non-Multicurrency Account',
            help="Check Accounts that were not set as multicurrency, "
            "i.e., they were not set with a secondary currency, "
            "but were involved in multicurrency transactions"),
    }
