# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Nhomar <nhomar@vauxoo.com>
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

import datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class crossovered_budget(osv.osv):
    _inherit = "crossovered.budget"
    _description = "Budget"

    _columns = {
        'dt_approved': fields.date('Date Approved',
                                   states={'done': [('readonly', True)]}),
        'dt_validated': fields.date('Date Validated',
                                    states={'done': [('readonly', True)]}),
        'period_id': fields.many2one('account.period', 'Period',
                                     domain=[('special', '<>', True)],
                                     help="Period for this budget"),
        'dt_done': fields.date('Date Done',
                               states={'done': [('readonly', True)]}),
    }

class crossovered_budget_lines(osv.osv):
    _inherit = 'crossovered.budget.lines'

    def _prac_acc(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = self._prac_amt_acc(cr, uid, [line.id], context=context)[line.id]
        return res

    _columns = {
        'practical_amount_aa': fields.function(_prac_acc,
                              string='Caused Amount', type='float',
                              digits_compute=dp.get_precision('Account')),
        'period_id': fields.many2one('account.period', 'Period',
                                     domain=[('special', '<>', True)],
                                     help="Period for this budget"),
        'forecasted_amount': fields.float('Forecasted Amount',
                           digits_compute=dp.get_precision('Account'),
                           help="Due to your analisys what is the amopunt that the manager stimate will comply to be compared with the Planned Ammount"),
    }

    def _prac_amt_acc(self, cr, uid, ids, context=None):
        '''
        This Method should compute considering Accounts Accounts due to the 
        Account Analityc Account is not mandatory in the budget Line.
        If the account Analityc Account is empty 
        '''
        res = {}
        result = 0.0
        if context is None: 
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            acc_ids = [x.id for x in line.general_budget_id.account_ids]
            if not acc_ids:
                raise osv.except_osv(_('Error!'),_("The Budget '%s' has no accounts!") % str(line.general_budget_id.name))
            date_to = line.date_to
            date_from = line.date_from
            if context.has_key('wizard_date_from'):
                date_from = context['wizard_date_from']
            if context.has_key('wizard_date_to'):
                date_to = context['wizard_date_to']
            if line.analytic_account_id.id:
                cr.execute("SELECT SUM(amount) FROM account_analytic_line WHERE account_id=%s AND (date "
                       "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND "
                       "general_account_id=ANY(%s)", (line.analytic_account_id.id, date_from, date_to,acc_ids,))
                result = cr.fetchone()[0]
            else:
                result = sum([a.balance for a in line.general_budget_id.account_ids]) 
            if result is None:
                result = 0.00
            res[line.id] = result
        return res

