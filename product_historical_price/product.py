# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
##########################################################################
from openerp import models, fields

from openerp.addons.decimal_precision import decimal_precision as dp
import time


class ProductHistorical(models.Model):

    """product_historical
    """

    _inherit = 'product.template'

    list_price_historical_ids = fields.One2many('product.historic.price',
                                                'product_id',
                                                'Historical Prices',
                                                help='Historical changes '
                                                'of the sale price of '
                                                'this product')
    cost_historical_ids = fields.One2many('product.price.history',
                                          'product_template_id',
                                          'Historical Cost',
                                          help='Historical changes '
                                          'in the cost of this product')


class ProductHistoricPrice(models.Model):
    _order = "name desc"
    _name = "product.historic.price"
    _description = "Historical Price List"

    product_id = fields.Many2one('product.template',
                                 ondelete='cascade',
                                 string='Product related to this Price',
                                 required=True)
    name = fields.Datetime(string='Date',
                           default=lambda *a:
                           time.strftime('%Y-%m-%d %H:%M:%S'),
                           required=True)
    price = fields.Float(string='Price',
                         digits_compute=dp.get_precision('Price'))
    product_uom = fields.Many2one('product.uom', string="Supplier UoM",
                                  help="""Choose here the Unit of Measure
                                          in which the prices and
                                          quantities are expressed
                                          below.""")
