# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)
#    2004-2010 Tiny SPRL (<http://tiny.be>).
#    2009-2010 Veritos (http://veritos.nl).
#    All Rights Reserved
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
import operator as py_operator

from openerp import fields, models, api

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _compute_query(self, ids, query_type):
        obj = self.env['account.invoice']
        return obj._compute_query(ids, 'sale_id', query_type)

    @api.multi
    def _compute_pending_reconciliation(self):
        res = self._compute_query(self._ids, 'query1')
        for brw in self:
            brw.reconciliation_pending = res.get(brw.id, 0)

    def _search_pending_reconciliation(self, operator, value):
        res = self._compute_query(self.search([])._ids, 'query1')
        ids = [rec_id
               for (rec_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]
        return [('id', 'in', ids)]

    @api.multi
    def _compute_unreconciled_lines(self):
        res = self._compute_query(self._ids, 'query2')
        for brw in self:
            brw.unreconciled_lines = res.get(brw.id, 0)

    def _search_unreconciled_lines(self, operator, value):
        res = self._compute_query(self.search([])._ids, 'query2')
        ids = [rec_id
               for (rec_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]
        return [('id', 'in', ids)]

    unreconciled_lines = fields.Integer(
        compute='_compute_unreconciled_lines',
        search='_search_unreconciled_lines',
        help="Indicates how many unreconciled lines are still standing")
    reconciliation_pending = fields.Integer(
        compute='_compute_pending_reconciliation',
        search='_search_pending_reconciliation',
        help="Indicates how many possible reconciliations are pending")
    aml_ids = fields.One2many(
        'account.move.line', 'sale_id', 'Account Move Lines',
        help='Journal Entry Lines related to this Sale Order')

    def cron_sale_accrual_reconciliation(self):
        self.env['account.invoice'].cron_accrual_reconciliation('sale_id')

    @api.multi
    def reconcile_stock_accrual(self):
        self.env['account.invoice'].reconcile_stock_accrual(
            self._ids, 'sale_id')

    @api.multi
    def view_accrual(self):
        return self.env['account.invoice'].view_accrual(
            self._ids, 'sale.order')
