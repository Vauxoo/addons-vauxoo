# -*- coding: utf-8 -*-
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
        """Calculate if the stock picking have been generated via purchase order
        confirmation. If this is the case then the move lines of the picking
        will have purchase order lines associated. The purchase order and the
        change picking field are extract from the purchase order and added to
        two computational fields:
            - purchase_id
            - change_picking

        By default is there is not purchase order associated to the picking
        then the purchase_id field will be False and the change_picking field
        will be True. This last one means that any picking have the option to
        change its move lines at least it have associated a purchase order who
        explicit have the change picking False.
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

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        """Before call the wizard to enter the transfer defailts will check if the
        current picking move lines have been change from the purchase order.

        NOTE: This validation applies when trying to validate a picking from
        the odoo interface.
        """
        context = context or {}
        self.check_move_lines(cr, uid, picking, context=context)
        res = super(StockPicking, self).do_enter_transfer_details(
            cr, uid, picking, context=context)
        return res

    @api.multi
    def do_transfer(self):
        """Overwrite method used to transfer the picking to verify if the
        change_picking field is False and then check that the picking move
        lines match with the purchase order lines.
        """
        self.check_move_lines()
        res = super(StockPicking, self).do_transfer()
        return res

    @api.model
    def get_error_msg(self, ch_state='DIFFER'):
        """Return a string with the error message header to show when the change
        picking False option is set in the purchase order
        """
        return ' '.join([
            _('This transfer can not be done.'
              ' the related purchase order is mark with not change'
              ' picking and the current picking have'),
            ch_state, _('move lines')])

    @api.multi
    def check_move_lines(self):
        """This method check if the move lines match with the purchase order
        lines. Check if any move line have been addded, removed or edited.

        NOTE: Only apply when have a stock picking generated via purchase
        order confirmation and when the purchase order have been configured
        as change picking False.
        """
        if self.change_picking:
            return True

        purchase_lines = self.purchase_id.order_line
        lines = self.move_lines

        # check if added new moves
        added_lines = self.get_added_lines()
        if added_lines:
            raise exceptions.Warning(self.get_error_msg(_('NEW')))

        # check if missing purchase lines
        missing_lines = self.get_remove_lines()
        if missing_lines:
            raise exceptions.Warning(self.get_error_msg(_('REMOVE')))

        # check if edited the move lines
        move_lines = [
            (line.product_id, line.product_uom, line.product_uom_qty)
            for line in lines]
        purchase_lines = [
            (line.purchase_line_id.product_id,
             line.purchase_line_id.product_uom,
             line.purchase_line_id.product_qty)
            for line in lines]
        edited_lines = self.get_edited_lines(purchase_lines, move_lines)
        if edited_lines:
            raise exceptions.Warning(self.get_error_msg(_('EDITED')))

        return True

    @api.model
    def line_print(self, title, lines):
        """Print in logger the lines data.
        """
        return '\n' + '---- ' + title + '\n' + self.line2str(lines) + '\n'

    @api.model
    def line2str(self, lines):
        """Return a string human readable representation of the move line.
        """
        res = str()
        if isinstance(lines, list):
            res = '\n'.join([
                "- %(product)s %(qty)s %(uom)s" % dict(
                    product=line[0].name,
                    qty=line[2],
                    uom=line[1].name)
                for line in lines])
        else:
            model = str(lines._model)
            if model == 'stock.move':
                res = '\n'.join([
                    "- %(product)s %(qty)s %(uom)s" % dict(
                        product=line.product_id.name,
                        qty=line.product_uom_qty,
                        uom=line.product_uom.name)
                    for line in lines])
            elif model == 'purchase.order.line':
                res = '\n'.join([
                    "- %(product)s %(qty)s %(uom)s" % dict(
                        product=line.product_id.name,
                        qty=line.product_qty,
                        uom=line.product_uom.name)
                    for line in lines])

        if lines and not res:
            raise exceptions.Warning(lines._model)
        return res

    def get_added_lines(self):
        """Search the move lines added to the picking that are not related to a
        purchase order line.
        """
        move_lines = self.move_lines
        lines_w_pol = move_lines.filtered("purchase_line_id")
        lines_wo_pol = move_lines - lines_w_pol
        return lines_wo_pol

    def get_remove_lines(self):
        """Search between the purchase order lines and the picking move lines and
        return the remove move lines correspond to a purchase line.
        """
        move_lines = self.move_lines
        purchase_lines = self.purchase_id.order_line
        move_lines_pol = move_lines.mapped("purchase_line_id")
        missing_lines = purchase_lines - move_lines_pol
        return missing_lines

    def get_edited_lines(self, src_lines, new_lines):
        """Search when differ from purchase line, picking line, transfer line,
        """
        differ_lines = []
        for line in new_lines:
            if line not in src_lines:
                differ_lines.append(line)
        return differ_lines
