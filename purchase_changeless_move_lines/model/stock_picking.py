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

from openerp import models, fields, api, exceptions, _


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    change_picking = fields.Boolean(
        compute='_compute_purchase_fields',
        string='Change Picking',
        help="This field only apply to stock pickings related to purchase"
             " orders. If True can change the move lines. If False can not"
             " change the move lines this remains equal to the purchase order"
             " lines. This field value is defined in the purchase order"
             " itself")

    purchase_id = fields.Many2one(
        'purchase.order',
        compute='_compute_purchase_fields',
        string='Purchase Order',
        help="If this stock pickings was generated via a purchase order")

    @api.depends('move_lines', 'change_picking')
    def _compute_purchase_fields(self):
        """
        Calculate if the stock picking have lines generated via purchsae order
        """
        for record in self:
            change_picking = True
            order = False
            purchase_lines = record.move_lines.mapped('purchase_line_id')
            if purchase_lines:
                order = purchase_lines.mapped('order_id')
                if order and len(order) == 1:
                    change_picking = order.change_picking
                    order = order.id
                else:
                    raise exceptions.Warning(_(
                        'A stock picking with purchase lines of multiple'
                        ' purchase orders case is not implemented yet into'
                        ' purchase_chagenless_move_lines module.'))
            self.purchase_id = order
            self.change_picking = change_picking

    @api.multi
    def do_transfer(self):
        """
        Verify if the change_picking field and if is True then will check that
        no move lines have been edited, added or removed.
        """
        error_msg = _(
            'This transfer can not be done.'
            ' The related purchase order is mark with not change'
            ' picking and the current picking have ')
        if not self.change_picking:
            lines = self.move_lines

            # check if added new lines
            lines_w_pol = lines.filtered("purchase_line_id")
            lines_wo_pol = lines - lines_w_pol
            if lines_wo_pol:
                raise exceptions.Warning(error_msg + _('NEW move lines'))

            # check if removed lines
            purchase_lines = self.purchase_id.order_line
            move_lines_pol = lines.mapped("purchase_line_id")
            missing_lines = purchase_lines - move_lines_pol
            if missing_lines:
                raise exceptions.Warning(error_msg + _('REMOVE move lines'))

            # check if edited the move lines
            for line in lines:
                move_line = (line.product_id,
                             line.product_uom,
                             line.product_uom_qty)
                purchase_line = (line.purchase_line_id.product_id,
                                 line.purchase_line_id.product_uom,
                                 line.purchase_line_id.product_qty)
                if move_line != purchase_line:
                    raise exceptions.Warning(
                        error_msg + _('DIFFERENT move lines'))

        return super(StockPicking, self).do_transfer()
