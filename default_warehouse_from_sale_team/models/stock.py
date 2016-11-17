# coding: utf-8

from openerp import api, fields, models


class StockPickingType(models.Model):

    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'default.warehouse']


class StockPicking(models.Model):

    _name = "stock.picking"
    _inherit = ['stock.picking', 'default.warehouse']

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id')


class StockQuant(models.Model):

    _inherit = "stock.quant"

    @api.model
    def _get_accounting_data_for_valuation(self, move):

        journal_id, acc_src, acc_dest, acc_valuation = super(
            StockQuant, self)._get_accounting_data_for_valuation(move)

        sale_team = self.env['crm.case.section'].search(
            [('default_warehouse',
              '=',
              move.warehouse_id.id if move.warehouse_id
              else move.picking_type_id.warehouse_id.id)],
            limit=1)

        if sale_team.journal_stock_id:
            journal_id = sale_team.journal_stock_id.id

        return journal_id, acc_src, acc_dest, acc_valuation
