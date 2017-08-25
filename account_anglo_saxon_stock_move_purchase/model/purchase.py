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


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"
    query = '''
        SELECT purchase_id, SUM(qty)
        FROM (
            SELECT
                aml.purchase_id AS purchase_id,
                aml.product_id as product_id,
                aml.account_id as account_id,
                COUNT(aml.id) as qty
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                purchase_id IN %(ids)s
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY purchase_id, product_id, account_id
            HAVING ABS(SUM(aml.debit - aml.credit)) <= %(offset)s -- Threashold
            ) AS view
        GROUP BY purchase_id
        ;'''

    query2 = '''
        SELECT
            aml.purchase_id AS purchase_id,
            COUNT(aml.id) as qty
        FROM account_move_line aml
        INNER JOIN account_account aa ON aa.id = aml.account_id
        WHERE
            purchase_id IN %(ids)s
            AND product_id IS NOT NULL
            AND reconcile_id IS NULL
            AND aa.reconcile = TRUE
        GROUP BY purchase_id
        ;'''

    def _compute_query(self, ids, query):
        res = {}.fromkeys(ids, 0)
        company_id = self.env['res.users'].browse(self._uid).company_id
        query_params = {'ids': ids, 'offset': company_id.accrual_offset}
        self._cr.execute(query, query_params)
        res.update(dict(self._cr.fetchall()))
        return res

    @api.multi
    def _compute_pending_reconciliation(self):
        res = self._compute_query(self._ids, self.query)
        for brw in self:
            brw.reconciliation_pending = res.get(brw.id, 0)

    def _search_pending_reconciliation(self, operator, value):
        res = self._compute_query(self.search([])._ids, self.query)
        ids = [rec_id
               for (rec_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]

        return [('id', 'in', ids)]

    @api.multi
    def _compute_unreconciled_lines(self):
        res = self._compute_query(self._ids, self.query2)
        for brw in self:
            brw.unreconciled_lines = res.get(brw.id, 0)
        return

    def _search_unreconciled_lines(self, operator, value):
        res = self._compute_query(self.search([])._ids, self.query2)

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
        'account.move.line', 'purchase_id', 'Account Move Lines',
        help='Journal Entry Lines related to this Purchase Order')

    def cron_purchase_accrual_reconciliation(self):
        self.env['account.invoice'].cron_accrual_reconciliation('purchase_id')

    @api.multi
    def reconcile_stock_accrual(self):
        self.env['account.invoice'].reconcile_stock_accrual(
            self._ids, 'purchase_id')

    @api.multi
    def view_accrual(self):
        return self.env['account.invoice'].view_accrual(
            self._ids, 'purchase.order')
