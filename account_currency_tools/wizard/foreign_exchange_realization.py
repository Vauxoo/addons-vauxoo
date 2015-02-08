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

    def _get_fiscalyear(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        return self.pool.get('account.fiscalyear').find(
            cr, uid, exception=False, context=context)

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False,
                            context=None):
        res = {}
        res['value'] = {'period_id': False, 'period_ids': []}
        return res

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
            'account.account', 'act_bk_acc_rel',
            'account_id', 'act_id', 'Bank & Cash Accounts',
            domain=("[('type','=','liquidity'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Bank Accounts')),
        'rec_ids': fields.many2many(
            'account.account', 'act_rec_acc_rel',
            'account_id', 'act_id', 'Receivable Accounts',
            domain=("[('type','=','receivable'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Receivable Accounts')),
        'pay_ids': fields.many2many(
            'account.account', 'act_pay_acc_rel',
            'account_id', 'act_id', 'Payable Accounts',
            domain=("[('type','=','payable'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Payable Accounts')),
        'fiscalyear_id': fields.many2one(
            'account.fiscalyear', 'Fiscal Year',
            required=True,
            help='Fiscal Year'),
        'period_id': fields.many2one(
            'account.period', 'Period',
            required=True,
            domain=("[('fiscalyear_id','=',fiscalyear_id),"
                    "('special','=',False)]"),
            help=('Select your Payable Accounts')),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
        'currency_id': fields.many2one(
            'res.currency', 'Company Currency',
            help="This is currency used to post Journal Entry Lines"),
        'period_ids': fields.many2many(
            'account.period', 'act_period_acc_rel',
            'period_id', 'act_id', 'Affected Periods',
            readonly=True,
            help=('List of Affected Periods')),
    }

    _defaults = {
        'company_id': _get_default_company,
        'fiscalyear_id': _get_fiscalyear,
    }

    def action_get_periods(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ap_obj = self.pool.get('account.period')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        date_start = wzd_brw.fiscalyear_id.date_start
        date_stop = wzd_brw.period_id.date_stop
        res = ap_obj.search(
            cr, uid, [
                ('date_start', '>=', date_start),
                ('date_stop', '<=', date_stop)])
        if res:
            wzd_brw.write({'period_ids': [(6, wzd_brw.id, res)]})
        else:
            wzd_brw.write(
                {'period_ids': [(3, ap_brw.id) for ap_brw in
                                wzd_brw.period_ids]})
        return True

    def create_move(self, cr, uid, ids, context=None):
        return True
