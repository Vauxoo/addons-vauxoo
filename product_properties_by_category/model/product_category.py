# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Coded by: Hugo Adan <hugo@vauxoo.com>
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


class ProductCategory(models.Model):

    _inherit = 'product.category'

    @api.model
    def _get_selection(self):
        options = [
            ('1', 'Set True'),
            ('0', 'Set False'),
            ('-1', 'Not Set')
        ]
        return options

    purchase_requisition = fields.Selection(
        _get_selection,
        'Call for Bids',
        default='-1',
        help="Check this box to generate Call for Bids instead "
             "of generating requests for quotation from procurement.")


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.onchange('categ_id')
    def get_product_properties(self):
        """Reviews the state of the field product property in the product.category
        and update the default value of the corresponding fields in the
        product.template. If the category have not default value defined in the
        field will search into its parent categorty and so on until found a
        default value defined. If there is not default value defined will
        return False.

        - Check "Call of Bids" for the product.category and update the
          "Call for Bids" in the product.template.
        """
        self.purchase_requisition = self.get_purchase_requisition_default()

    @api.multi
    def get_purchase_requisition_default(self):
        """Add return the default value for the "Call for Bids" boolean field.
        """
        cr_categ_id = self.categ_id
        default_value = '-1'
        while cr_categ_id.parent_id:
            if cr_categ_id.purchase_requisition == '-1':
                cr_categ_id = cr_categ_id.parent_id
            else:
                default_value = cr_categ_id.purchase_requisition
                break
        return default_value != '-1' and bool(int(default_value)) or False
