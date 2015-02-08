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
from openerp.tools.translate import _


class foreign_exchange_realization(osv.osv_memory):

    _name = 'foreign.exchange.realization'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid,
                                                             context=context)
        if not company_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is no default company for the current user!'))
        return company_id

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        if context is None:
            context = {}
        context['company_id'] = company_id
        res = {'value': {}}

        if not company_id:
            return res

        cur_id = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context).currency_id.id
        res['value'].update({'currency_id': cur_id})
        return res

    _columns = {
        'help': fields.boolean(
            'Show Help', help='Allows you to toggle the help in the form'),
        'root_id': fields.many2one(
            'account.account', 'Root Account',
            domain=('[("company_id", "=", company_id), ("type", "=", "view"),'
                    '("parent_id", "=", None)]'),
            required=False,
            help=('Root Account, the account that plays as a'
                  'Chart of Accounts')),
        'bk_ids': fields.many2many(
            'account.account', 'acp_bk_acc_rel',
            'account_id', 'acp_id', 'Bank & Cash Accounts',
            domain=("[('type','=','liquidity'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Bank Accounts')),
        'rec_ids': fields.many2many(
            'account.account', 'acp_rec_acc_rel',
            'account_id', 'acp_id', 'Receivable Accounts',
            domain=("[('type','=','receivable'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Receivable Accounts')),
        'pay_ids': fields.many2many(
            'account.account', 'acp_pay_acc_rel',
            'account_id', 'acp_id', 'Payable Accounts',
            domain=("[('type','=','payable'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Payable Accounts')),
        'period_id': fields.many2one(
            'account.period', 'Period', required=True),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
        'currency_id': fields.many2one(
            'res.currency', 'Company Currency',
            help="This is currency used to post Journal Entry Lines"),
    }

    _defaults = {
        'company_id': _get_default_company,
    }

    def create_move(self, cr, uid, ids, context=None):
        return True
