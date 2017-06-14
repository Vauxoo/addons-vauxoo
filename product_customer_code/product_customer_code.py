# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, fields, api


class ProductCustomerCode(models.Model):
    _name = "product.customer.code"
    _description = "Add manies Code of Customer's"

    _rec_name = 'product_code'

    product_code = fields.Char('Customer Product Code', size=64, required=True,
                               help="""This customer's product code will be
                               used when searching into a request for
                               quotation.""")

    product_name = fields.Char('Customer Product Name', size=128,
                               help="""This customer's product name will
                               be used when searching into a request for
                               quotation.""")

    product_id = fields.Many2one('product.product', 'Product', required=True,
                                 help='Product Identification')

    partner_id = fields.Many2one('res.partner', 'Customer', required=True,
                                 help='Partner Reference')

    company_id = fields.Many2one('res.company', 'Company',
                                 help='Company Reference',
                                 )

    @api.model
    def default_get(self, default_fields):
        rec = super(ProductCustomerCode, self).default_get(default_fields)
        if rec['company_id']:
            rec['company_id'] = (
                self.env['res.company']._company_default_get(
                    'product.customer.code'))
        return rec

    _sql_constraints = [
        ('unique_code', 'unique(product_code,company_id,partner_id)',
         'Product Code of customer must be unique'),
    ]

# TODO: Add index to product_code, partner_id
