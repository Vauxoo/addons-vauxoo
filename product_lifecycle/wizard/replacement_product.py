# -*- encoding: utf-8 -*-
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


class ReplacementProduct(models.TransientModel):

    """
    Wizard that let to select one of the replacement product of a discontinued
    product.
    """

    _name = 'replacement.product'
    _description = 'Select a replacement product for purchase operations'

    product_id = fields.Many2one(
        'product.template', 'Discontinued Product',
        default=lambda self: self._context.get('discontinued_product_id',
                                               False))
    replacement_product_id = fields.Many2one(
        'product.template', string='Replacement Product for Purchase')

    @api.onchange('product_id')
    def get_replacement_product_ids(self):
        """
        Return the list of replacment products
        @return domain
        """
        self.replacement_product_id = False
        res = {'domain': {'replacement_product_id': [('id', 'in', [])]}}
        replacement_ids = [
            product.id for product in self.product_id.replacement_product_ids]
        if replacement_ids:
            if len(replacement_ids) == 1:
                self.replacement_product_id = replacement_ids[0]
            res = {'domain': {
                'replacement_product_id': [('id', 'in', replacement_ids)]}}
        return res

    @api.multi
    def select_replacement(self):
        """
        Return the replacement product.
        """
        return self.replacement_product_id
