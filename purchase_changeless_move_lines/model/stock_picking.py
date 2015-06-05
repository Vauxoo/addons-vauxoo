# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral <kathy@vauxoo.com>
#    Audited by: Katherine Zaoral <kathy@vauxoo.com>
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning  # pylint: disable=W0622


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    purchase_id = fields.Many2one(
        'purchase.order',
        compute='_compute_purchase_order_id',
        string='Purchase Order',
        help="If this stock pickings was generated via a purchase order")

    @api.depends('move_lines')
    def _compute_purchase_order_id(self):
        """
        Calculate if the stock picking have lines generated via purchsae order
        """
        for record in self:
            order = False
            purchase_lines = record.move_lines.mapped('purchase_line_id')
            if purchase_lines:
                order = purchase_lines.mapped('order_id')
                if order and len(order) == 1:
                    order = order.id
                else:
                    raise Warning(_(
                        'A stock picking with purchase lines of multiple'
                        ' purchase orders case is not implemented yet into'
                        ' purchase_chagenless_move_lines module.'))
            self.purchase_id = order
