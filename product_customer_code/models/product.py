# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com),Moy (moylop260@vauxoo.com)
############################################################################
#    Migrated to v10 by: Miguel Paraiso (miguel.paraiso@aselcis.com)
#    Aselcis Consulting (http://www.aselcis.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_customer_code_ids = fields.One2many('product.customer.code', 'product_id', 'Customer Codes')

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        default['product_customer_code_ids'] = False
        res = super(ProductProduct, self).copy(default=default)
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(ProductProduct, self).name_search(name, args, operator, limit)
        if not res:
            partner_id = self._context.get('partner_id')
            if partner_id:
                prod_code = self.env['product.customer.code'].search([('product_code', '=', name),
                                                                      ('partner_id', '=', partner_id)], limit=limit)
                # TODO: Search for product customer name
                if prod_code:
                    res = prod_code.name_get()
        return res
