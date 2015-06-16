# -*- encoding: utf-8 -*-
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

    purchase_requisition = fields.Selection([
        ('1', "Set True"),
        ('0', "Set False"),
        ('-1', "Not Set"),
    ], default='-1')


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.onchange('categ_id')
    def _get_prod_cate_call_of_bids(self):
        """
        Reviews the state of the field "Call of Bids" in the product.category
        and update the state of the field "Call of Bids"
        in the product.template (Boolean field with the same name).
        If the field purchase_requisition product.category has "Not Set" option
        then review the product category father
        and so on until you find a category where you have defined
         (other than 'Not Set') value.
        """
        self.purchase_requisition = self.check_parents_prch_rqs(self.categ_id)

    @api.one
    def check_parents_prch_rqs(self, categ_id):
        if categ_id:
            if categ_id.purchase_requisition == '-1':
                self.check_parents_prch_rqs(categ_id.parent_id)
            else:
                return categ_id.purchase_requisition
        else:
            return False
