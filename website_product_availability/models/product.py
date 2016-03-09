# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.tools.float_utils import float_round


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    consider_on_request = fields.Boolean(
        'Route On Request',
        help='Checking this you will '
             'consider this route as an '
             '\'On Request\' route, this means '
             'that every product that has this '
             'route assigned will show on the '
             'website the legend \'On Request\' '
             'on the availability field, '
             'please be careful to set up this '
             'route.')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_states(self):
        return [
            ('1', 'Available'),
            ('2', 'Not Available'),
            ('3', 'Low Availability'),
            ('4', 'On Request'),
        ]

    @api.multi
    @api.depends('qty_available', 'low_stock')
    def _get_availability(self):
        for record in self:
            product = record
            for route in product.route_ids:
                if route.consider_on_request:
                    product.stock_state = '4'
                    return
            product.stock_state = self._get_availability_by_qty(
                product.qty_available, product.low_stock)

    def _get_availability_by_qty(self, qtys, low_stock):
        if qtys > low_stock:
            return '1'
        elif 0 < qtys <= low_stock:
            return '3'
        elif qtys <= 0:
            return '2'

    low_stock = fields.Integer(
        'Low Stock',
        help='This field is used to show '
        'on the website when a product has '
        'low availability, any number of stock'
        'equals the value set or lower will show '
        '\'low avilability\' on product')
    stock_state = fields.Selection(
        compute=_get_availability,
        selection=get_states,
        string="Website Stock State",
        default=0)

    @api.multi
    def _get_locations_quants(self):
        for record in self:
            stock_locations_obj = self.env['location.quants']
            stock_quants_obj = self.env['stock.quant']
            product_id = record.id
            quants = stock_quants_obj.search(
                [('product_id', '=', product_id),
                 ('location_id.usage', '=', 'internal')])
            stock_locations_ids = quants.mapped('location_id')
            new_quants = []
            product = record
            for location in stock_locations_ids:
                qtys = self.with_context(
                    location=location.id)._product_available(None, False)
                new_qty = qtys.get(product_id).get('qty_available')
                stock_state = '2'
                for route in product.route_ids:
                    if route.consider_on_request:
                        stock_state = '4'
                        break
                if stock_state != '4':
                    stock_state = self._get_availability_by_qty(
                        product.qty_available, product.low_stock)
                location_ok = stock_locations_obj.search(
                    [('product_id', '=', product_id),
                     ('location_id', '=', location.id)])
                if location_ok:
                    if location_ok.qty != new_qty:
                        location_ok.write(
                            {'qty': new_qty,
                             'stock_state': stock_state})
                    new_quants.append(location_ok.id)
                else:
                    new_id = stock_locations_obj.create(
                        {'product_id': product_id,
                         'location_id': location.id,
                         'qty': new_qty,
                         'stock_state': stock_state})
                    new_quants.append(new_id.id)
            record.product_stock_quants_ids = new_quants

    @api.multi
    def _get_planned_dates(self):
        for record in self:
            pol_obj = self.env['purchase.order.line']
            product_id = record.id
            pol_ids = pol_obj.search([('product_id', '=', product_id),
                                      ('state', 'in', ('draft', 'confirmed'))])
            record.product_planned_dates_ids = pol_ids

    product_stock_quants_ids = fields.One2many(
        compute=_get_locations_quants,
        comodel_name='location.quants',
        inverse_name='product_id',
        string='Locations Quants',)
    product_planned_dates_ids = fields.One2many(
        compute=_get_planned_dates,
        comodel_name='purchase.order.line',
        inverse_name='product_id',
        string='Locations Quants')

    @api.multi
    def _product_availability_warehouse(self, warehouse_id):
        # search avalailability for stokable products
        if self.type != 'product':
            return True
        domain_quant = []
        product = self
        domain_quant += [('product_id', 'in', [product.id])]
        domain_quant_loc = product.with_context(
            warehouse=warehouse_id.id)._get_domain_locations()[0]
        domain_quant += domain_quant_loc
        quants = self.env['stock.quant'].read_group(
            domain_quant, ['product_id', 'qty'],
            ['product_id'])
        quants = dict([(x['product_id'][0], x['qty']) for x in quants])
        qty_available = float_round(
            quants.get(product.id, 0.0),
            precision_rounding=product.uom_id.rounding)
        return qty_available


class LocationQuants(models.Model):
    _name = 'location.quants'

    def get_states(self):
        return [
            ('1', 'Available'),
            ('2', 'Not Available'),
            ('3', 'Low Availability'),
            ('4', 'On Request'),
        ]

    product_id = fields.Many2one('product.product', 'Product')
    location_id = fields.Many2one('stock.location', 'Stock Location')
    qty = fields.Float('Quantity')
    stock_state = fields.Selection(
        selection=get_states,
        string="Website Stock State",
        default=0)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    stock_alias = fields.Char('Alias Stock', default="Set Alias name")
    website_published = fields.Boolean(
        'Available in the website', copy=False)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    stock_alias = fields.Char(
        'Alias Stock', default="Set Alias name",
        help='Alias name to display in website')
    website_published = fields.Boolean(
        'Available in the website', copy=False)
