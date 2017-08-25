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
import logging
import operator as py_operator
import time

from openerp.osv import orm
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_is_zero

_logger = logging.getLogger(__name__)

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
                purchase_id IN %s
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY purchase_id, product_id, account_id
            HAVING ABS(SUM(aml.debit - aml.credit)) <= %s -- Use Threashold
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
            purchase_id IN %s
            AND product_id IS NOT NULL
            AND reconcile_id IS NULL
            AND aa.reconcile = TRUE
        GROUP BY purchase_id
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

        ids = [purchase_id
               for (purchase_id, computed_value) in res.items()
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

        ids = [purchase_id
               for (purchase_id, computed_value) in res.items()
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

    def cron_purchase_accrual_reconciliation(self, cr, uid, context=None):
        _logger.info('Reconciling Purchase Order Stock Accruals')
        company_id = self.pool['res.users'].browse(cr, uid, uid).company_id
        cr.execute('''
            SELECT
                aml.purchase_id AS id,
                aml.product_id as product_id,
                aml.account_id as account_id,
                COUNT(aml.id) as count
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                purchase_id IS NOT NULL
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY purchase_id, product_id, account_id
            HAVING COUNT(aml.id)  > 1
            AND ABS(SUM(aml.debit - aml.credit)) <= %s -- Use Threashold
            ;
            ''', (company_id.accrual_offset,))

        ids = list(set(x[0] for x in cr.fetchall()))
        if not ids:
            return
        self.browse(cr, uid, ids, context=context).reconcile_stock_accrual()

        return

    @api.multi
    def reconcile_stock_accrual(self):
        self.env['account.invoice'].reconcile_stock_accrual(
            self._ids, 'purchase_id')

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
