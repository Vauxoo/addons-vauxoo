# -*- coding: utf-8 -*-

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    date_stock_account_border = fields.Datetime(
        string='Stock Account Border Date',
        help='Used when computing average for products that are returned'
        'from Customers and whose date are prior to Initialization Inventory',
    )
