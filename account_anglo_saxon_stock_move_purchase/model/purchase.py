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
from openerp import fields, models, api


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    # /!\ NOTE: Following two methods can be drawn from a TransientModel
    # instead of account.invoice
    def _compute_value(self, name, query_type):
        self.env['account.invoice']._compute_value(
            self._ids, name, query_type, 'purchase_id')

    def _compute_search(self, name, query_type, operator, value):
        return self.env['account.invoice']._compute_search(
            name, query_type, 'purchase_id', operator, value)

    @api.multi
    def _compute_pending_reconciliation(self):
        self._compute_value('reconciliation_pending', 'query1')

    def _search_pending_reconciliation(self, operator, value):
        return self._compute_search(
            'reconciliation_pending', 'query1', operator, value)

    @api.multi
    def _compute_unreconciled_lines(self):
        self._compute_value('unreconciled_lines', 'query2')

    def _search_unreconciled_lines(self, operator, value):
        return self._compute_search(
            'unreconciled_lines', 'query2', operator, value)

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
