#!/usr/bin/python
# -*- encoding: utf-8 -*-
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


class res_company(osv.Model):
    _inherit = "res.company"
    _description = 'Companies'

    _columns = {
        'bank_gain_loss_exchange_account_id': fields.many2one(
            'account.account', 'Bank Gain or Loss Exchange Rate Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Bank Gain or Loss Exchange Rate Account for booking '
                  'Difference')),
        'rec_gain_loss_exchange_account_id': fields.many2one(
            'account.account', 'Receivable Gain or Loss Exchange Rate Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Receivable Gain or Loss Exchange Rate Account for booking '
                  'Difference')),
        'pay_gain_loss_exchange_account_id': fields.many2one(
            'account.account', 'Payable Gain or Loss Exchange Rate Account',
            domain=('[("type", "!=", "view")]'),
            required=False,
            help=('Payable Gain or Loss Exchange Rate Account for booking '
                  'Difference')),
    }
