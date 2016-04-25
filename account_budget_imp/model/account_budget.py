# coding: utf-8
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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


class CrossoveredBudget(osv.osv):
    _inherit = "crossovered.budget"
    _description = "Budget"

    _columns = {
        'dt_approved': fields.date('Date Approved',
                                   readonly=True),
        'dt_validated': fields.date('Date Validated',
                                    readonly=True),
        'dt_done': fields.date('Date Done',
                               readonly=True,
                               help="Date when the cicle finish."),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year',
                                         help="Period for this budget"),
        'period_id': fields.many2one('account.period', 'Period',
                                     help="Period for this budget"),
        'date_from': fields.date('Start Date', states={'done': [('readonly', True)]}),
        'date_to': fields.date('End Date', states={'done': [('readonly', True)]}),
        'company_id': fields.many2one('res.company', 'Company'),
        'general_budget_id': fields.many2one('account.budget.post', 'Budgetary Position'),
    }

    _default = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }


class CrossoveredBudgetLines(osv.osv):
    _inherit = 'crossovered.budget.lines'

    def _prac_acc(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = self._prac_amt_acc(
                cr, uid, [line.id], context=context)[line.id]
        return res

    def _get_ifrs_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        cbl_brws = self.browse(cr, uid, ids, context=context)
        ifrs_line_obj = self.pool.get('ifrs.lines')
        for line in cbl_brws:
            ifrs_result = ifrs_line_obj._get_amount_value(cr, uid,
                                                          [line.ifrs_lines_id.id],
                                                          ifrs_line=line.ifrs_lines_id,
                                                          period_info=line.period_id,
                                                          context=context)
            res[line.id] = ifrs_result
        return res

    _columns = {
        'practical_amount_aa': fields.function(_get_ifrs_total,
                                               string='Caused Amount', type='float',
                                               digits_compute=dp.get_precision(
                                                   'Account'),
                                               help="This amount comes from the computation related to the IFRS line report related"),
        'practical_amount': fields.function(_prac_acc,
                                            string='Amount', type='float',
                                            digits_compute=dp.get_precision('Account')),
        'theoritical_amount': fields.function(_prac_acc,
                                              string='Amount', type='float',
                                              digits_compute=dp.get_precision('Account')),
        'forecasted_amount': fields.float('Forecasted Amount',
                                          digits_compute=dp.get_precision(
                                              'Account'),
                                          help="""Due to your analisys what is the amopunt that
                           the manager stimate will comply to be compared with
                           the Planned Ammount"""),
        'ifrs_lines_id': fields.many2one("ifrs.lines", "Report Line",
                                         help="Line on the IFRS report to analyse your budget."),
        'period_id': fields.many2one('account.period', 'Period',
                                     domain=[('special', '<>', True)],
                                     help="Period for this budget"),
        'date_from': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
    }

    _default = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def write(self, cr, uid, ids, values, context=None):
        period_brw = self.pool.get('account.period').browse(
            cr, uid, values.get('period_id'), context=context)
        values.update({'date_from': period_brw.date_start,
                       'date_to': period_brw.date_stop})
        return super(CrossoveredBudgetLines, self).write(cr, uid, ids, values, context=context)

    def create(self, cr, uid, values, context=None):
        period_brw = self.pool.get('account.period').browse(
            cr, uid, values.get('period_id'), context=context)
        values.update({'date_from': period_brw.date_start,
                       'date_to': period_brw.date_stop})
        return super(CrossoveredBudgetLines, self).create(cr, uid, values, context=context)

    def _prac_amt_acc(self, cr, uid, ids, context=None):
        """This Method should compute considering Accounts Accounts due to the
        Account Analityc Account is not mandatory in the budget Line.
        If the account Analityc Account is empty
        """
        res = {}
        result = 0.0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            date_to = line.date_to
            date_from = line.date_from
            if context.has_key('wizard_date_from'):
                date_from = context['wizard_date_from']
            if context.has_key('wizard_date_to'):
                date_to = context['wizard_date_to']
            if not date_from or not date_to:
                acc_b_ids = line.general_budget_id and line.general_budget_id.account_ids or []
                acc_ids = [x.id for x in acc_b_ids]
                if not acc_ids:
                    result = 0.00
                if line.analytic_account_id.id:
                    cr.execute("SELECT SUM(amount) FROM account_analytic_line WHERE account_id=%s AND (date "
                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND "
                               "general_account_id=ANY(%s)", (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                    result = cr.fetchone()[0]
                else:
                    result = sum(
                        [a.balance for a in line.general_budget_id.account_ids])
            else:
                result = 0.00
            if result is None:
                result = 0.00
            res[line.id] = result
        return res
