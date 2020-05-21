# coding: utf-8
from odoo import fields, models, api


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
    def _compute_to_be_reconciled(self):
        self._compute_value('to_be_reconciled', 'query1')

    def _search_to_be_reconciled(self, operator, value):
        return self._compute_search(
            'to_be_reconciled', 'query1', operator, value)

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
    to_be_reconciled = fields.Integer(
        compute='_compute_to_be_reconciled',
        search='_search_to_be_reconciled',
        help="Indicates how many possible reconciliations are pending")
    aml_ids = fields.One2many(
        'account.move.line', 'purchase_id', 'Account Move Lines',
        help='Journal Entry Lines related to this Purchase Order')

    @api.model
    def cron_purchase_accrual_reconciliation(self, do_commit=False):
        self.env['account.invoice'].cron_accrual_reconciliation(
            'purchase_id', do_commit=do_commit)

    @api.multi
    def reconcile_stock_accrual(self):
        self.env['account.invoice'].reconcile_stock_accrual(
            self._ids, 'purchase_id')

    @api.multi
    def view_accrual(self):
        return self.env['account.invoice'].view_accrual(
            self._ids, 'purchase.order')
