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

from openerp import models, api, exceptions


class StockTransferDetails(models.TransientModel):

    _inherit = 'stock.transfer_details'

    @api.multi
    def do_detailed_transfer(self):
        """Before transfer the picking move lines will check if the transfer lines
        differ from the move lines.
        """
        self.ensure_one()
        self.check_transfer_lines()
        res = super(StockTransferDetails, self).do_detailed_transfer()
        return res

    @api.multi
    def check_transfer_lines(self):
        """This method check if the transfer move lines differ from the move lines
        and if is True raise and exception.
        """
        differ_lines = []
        picking = self.env['stock.picking']
        move_lines = [
            (line.product_id, line.product_uom, line.product_uom_qty)
            for line in self.picking_id.move_lines]
        transfer_lines = [
            (line.product_id, line.product_uom_id, line.quantity)
            for line in self.item_ids]

        remove_lines = self.get_edited_lines(transfer_lines, move_lines)
        if remove_lines:
            error_msg = ''.join([
                picking.get_error_msg('REMOVE move lines'), ':\n',
                picking.line2str(remove_lines)])
            raise exceptions.Warning(error_msg)

        differ_lines = self.get_edited_lines(move_lines, transfer_lines)
        if differ_lines:
            error_msg = ''.join([
                picking.get_error_msg(), ':\n',
                picking.line2str(differ_lines)])
            raise exceptions.Warning(error_msg)
        return True

    def get_edited_lines(self, src_lines, dest_lines):
        """Return differ between the groups of lines.
        """
        picking = self.env['stock.picking']
        return picking.get_edited_lines(src_lines, dest_lines)

    def line_print(self, title, lines):
        """Same as picking
        """
        picking = self.env['stock.picking']
        return picking.line_print(title, lines)
