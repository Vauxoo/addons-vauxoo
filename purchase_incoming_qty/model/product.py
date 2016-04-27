# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    purchase_incoming_qty = fields.Float(
        string='Purchase Incoming Qty',
        compute='_compute_purchase_incoming_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity of products that are planned to arrive result of"
             " purchase operations.")

    @api.depends('incoming_qty')
    def _compute_purchase_incoming_qty(self):
        """When the Incoming Qty is update then Purchase Incoming Qty is
        calculate. This Qty is calculated taking into account the purchase
        incoming qty of every product variant
        """
        for record in self:
            record.purchase_incoming_qty = sum([
                product.purchase_incoming_qty
                for product in record.product_variant_ids])


class ProductProduct(models.Model):

    _inherit = 'product.product'

    purchase_incoming_qty = fields.Float(
        string='Purchase Incoming Qty',
        compute='_compute_purchase_incoming_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity of products that are planned to arrive result of"
             " purchase operations.")

    @api.depends('incoming_qty')
    def _compute_purchase_incoming_qty(self):
        """Count the product qty in moves related to purchase lines.
        """
        for record in self:
            domain_move_in_pur = [
                ('product_id', '=', record.id),
                ('purchase_line_id', '!=', False),
                ('state', 'in', ['draft', 'waiting', 'assigned', 'confirmed']),
            ]
            moves = self.env['stock.move'].search(domain_move_in_pur)
            record.purchase_incoming_qty = sum(moves.mapped('product_qty'))
