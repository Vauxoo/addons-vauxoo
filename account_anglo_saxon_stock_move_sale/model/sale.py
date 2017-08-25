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

from openerp import fields, models, api, _

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
    query = '''
        SELECT sale_id, SUM(qty)
        FROM (
            SELECT
                aml.sale_id AS sale_id,
                aml.product_id as product_id,
                aml.account_id as account_id,
                COUNT(aml.id) as qty
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                sale_id IN %s
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY sale_id, product_id, account_id
            HAVING ABS(SUM(aml.debit - aml.credit)) <= %s -- Use Threashold
            ) AS view
        GROUP BY sale_id
        ;'''

    query2 = '''
        SELECT
            aml.sale_id AS sale_id,
            COUNT(aml.id) as qty
        FROM account_move_line aml
        INNER JOIN account_account aa ON aa.id = aml.account_id
        WHERE
            sale_id IN %s
            AND product_id IS NOT NULL
            AND reconcile_id IS NULL
            AND aa.reconcile = TRUE
        GROUP BY sale_id
        ;'''

    @api.multi
    def _compute_pending_reconciliation(self):

        company_id = self.env['res.users'].browse(self._uid).company_id
        offset = company_id.accrual_offset

        self._cr.execute(self.query, (tuple(self._ids), offset))
        res = dict(self._cr.fetchall())

        for brw in self:
            brw.reconciliation_pending = res.get(brw.id, 0)

        return

    def _search_pending_reconciliation(self, operator, value):
        ids = self.search([])._ids
        res = {}.fromkeys(ids, 0)
        company_id = self.env['res.users'].browse(self._uid).company_id
        offset = company_id.accrual_offset
        self._cr.execute(self.query, (tuple(ids), offset))

        res.update(dict(self._cr.fetchall()))

        ids = [sale_id
               for (sale_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]

        return [('id', 'in', ids)]

    @api.multi
    def _compute_unreconciled_lines(self):
        self._cr.execute(self.query2, (tuple(self._ids),))
        res = dict(self._cr.fetchall())
        for brw in self:
            brw.unreconciled_lines = res.get(brw.id, 0)
        return

    def _search_unreconciled_lines(self, operator, value):
        ids = self.search([])._ids
        res = {}.fromkeys(ids, 0)

        self._cr.execute(self.query2, (tuple(ids),))
        res.update(dict(self._cr.fetchall()))

        ids = [sale_id
               for (sale_id, computed_value) in res.items()
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

    def cron_sale_accrual_reconciliation(self, cr, uid, context=None):
        self.pool['account.invoice'].cron_accrual_reconciliation(
            cr, uid, [], 'sale_id')

    @api.multi
    def reconcile_stock_accrual(self):
        self.env['account.invoice'].reconcile_stock_accrual(
            self._ids, 'sale_id')

    def view_accrual(self, cr, uid, ids, context=None):
        ids = [ids] if isinstance(ids, (int, long)) else ids
        context = context or {}
        res = []
        for brw in self.browse(cr, uid, ids, context=context):
            res += [aml_brw.id
                    for aml_brw in brw.aml_ids
                    # This shall be taken away when fixing domain in aml_ids
                    if aml_brw.account_id.reconcile
                    ]
        return {
            'domain': "[('id','in',\
                [" + ','.join([str(item) for item in res]) + "])]",
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
