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


class ProductCustomerCode(models.Model):
    _name = "product.customer.code"
    _description = "Add manies Code of Customer's"
    _rec_name = 'product_code'

    product_code = fields.Char('Customer Product Code', size=64, required=True,
                               help="This customer's product code will be used when searching into a request for quotation.")
    product_name = fields.Char('Customer Product Name', size=128,
                               help="This customer's product name will be used when searching into a request for quotation.")
    product_id = fields.Many2one('product.product', 'Product', required=True)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('product.customer.code'))

    _sql_constraints = [
        ('unique_code', 'unique(product_code,company_id,partner_id)',
         'Product Code of customer must be unique'),
    ]

    # TODO: Add index to product_code, partner_id
