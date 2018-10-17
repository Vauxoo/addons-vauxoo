# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, _
_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.product"

    def action_view_stock_card(self):
        self.ensure_one()
        # Get lead views
        tree_view = self.env.ref(
            'stock_cost_segmentation.view_stock_move_cost')
        return {
            'name': _('Stock Card'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.move',
            'domain': [('product_id', '=', self.id),
                       ('state', '=', 'done')],
            'view_id': tree_view.id,
            'views': [
                (tree_view.id, 'tree'),
            ],
            'type': 'ir.actions.act_window',
        }

    def action_view_historical_lines(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_cost_segmentation.'
            'stock_historical_lines_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action

    def _get_fifo_logistic_candidates_in_move(self, warehouse):
        """ Find IN moves that can be used to value OUT moves.
        """
        self.ensure_one()
        domain = [('product_id', '=', self.id),
                  ('logistic_remaining_qty', '>', 0.0),
                  '|',
                  ('warehouse_id', '=', warehouse.id),
                  ('picking_type_id.warehouse_id', '=', warehouse.id)
                  ] + self.env['stock.move']._get_in_base_domain()
        candidates = self.env['stock.move'].search(domain, order='date, id')
        return candidates


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    material_cost = fields.Float(
        string='Material Cost', readonly=True)
    production_cost = fields.Float(
        string='Production Cost', readonly=True)
    subcontracting_cost = fields.Float(
        string='Subcontracting Cost', readonly=True)
    landed_cost = fields.Float(
        string='Landed Cost', readonly=True)

    def action_view_historical_lines(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_cost_segmentation.'
            'stock_historical_lines_action').read()[0]
        action['domain'] = [('product_id.product_tmpl_id', 'in', self.ids)]
        return action

    def action_view_stock_card(self):
        self.ensure_one()
        # Get lead views
        tree_view = self.env.ref(
            'stock_cost_segmentation.view_stock_move_cost')
        return {
            'name': _('Stock Card'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.move',
            'domain': [('product_id.product_tmpl_id', 'in', self.ids),
                       ('state', '=', 'done')],
            'view_id': tree_view.id,
            'views': [
                (tree_view.id, 'tree'),
            ],
            'type': 'ir.actions.act_window',
        }
