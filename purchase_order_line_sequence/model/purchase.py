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
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.one
    @api.constrains('order_line')
    def _check_order_lines_sequence(self):
        """check that the sequence is unique per purchase order line.
        """
        all_sequences = self.order_line.mapped('sequence')
        sequences = list(set(all_sequences))
        if len(all_sequences) != len(sequences):
            raise ValidationError(
                _('The sequence must be unique per purchase order!') + ".\n" +
                _('The next sequence numbers are already used') + ":\n" +
                str(sequences))


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'
    _order = "sequence"

    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence of this line when displaying the"
             " purchase order.")

    @api.model
    def default_get(self, fields_list):
        """Overwrite the default value of the sequence field taking into account
        the current number of lines in the purchase order. If is not call from
        the purchase order will use the default value.
        """
        res = super(PurchaseOrderLine, self).default_get(fields_list)
        res.update({'sequence': len(self._context.get('order_line', [])) + 1})
        return res
