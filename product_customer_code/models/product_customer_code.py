# coding: utf-8

from openerp import api, fields, models


class ProductCustomerCode(models.Model):

    _name = "product.customer.code"
    _description = "Add manies Code of Customer's"

    _rec_name = 'product_code'

    product_code = fields.Char('Customer Product Code', required=True,
                               index=True, help="""This customer's product
                               code will be used when searching into a request
                               for quotation.""")
    product_name = fields.Char('Customer Product Name', help="""This customer's
                               product name will be used when searching into a
                               request for quotation.""")
    product_id = fields.Many2one('product.product', 'Product', required=True,
                                 help='Product Identification')
    partner_id = fields.Many2one('res.partner', 'Customer', required=True,
                                 index=True, help='Partner Reference')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self:
                                 self._get_user_default_company())

    @api.model
    def _get_user_default_company(self):
        """Return the default company for the current user"""
        return self.env.user.company_id

    _sql_constraints = [
        ('unique_code', 'unique(product_code,company_id,partner_id)',
         'Product Code of customer must be unique'),
    ]
