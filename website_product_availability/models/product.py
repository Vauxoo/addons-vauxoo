# -*- coding:utf-8 -*-
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

    @api.one
    @api.depends('qty_available', 'low_stock')
    def _get_availability(self):
        product = self
        for route in product.route_ids:
            if route.consider_on_request:
                product.stock_state = '4'
                return
        if product.qty_available > product.low_stock:
            product.stock_state = '1'
        elif 0 < product.qty_available <= product.low_stock:
            product.stock_state = '3'
        elif product.qty_available <= 0:
            product.stock_state = '2'

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

    @api.one
    def _get_locations_quants(self):
        stock_locations_obj = self.env['location.quants']
        stock_quants_obj = self.env['stock.quant']
        product_id = self.id
        quants = stock_quants_obj.search(
            [('product_id', '=', product_id),
             ('location_id.usage', '=', 'internal')])
        stock_locations_ids = []
        for quant in quants:
            if quant.location_id.id in stock_locations_ids:
                continue
            stock_locations_ids.append(quant.location_id.id)
        new_quants = []
        product = self
        for location in stock_locations_ids:
            qtys = self.with_context(
                location=location)._product_available(None, False)
            new_qty = qtys.get(product_id).get('qty_available')
            stock_state = '2'
            for route in product.route_ids:
                if route.consider_on_request:
                    stock_state = '4'
                    break
            if stock_state != '4':
                if new_qty > product.low_stock:
                    stock_state = '1'
                elif 0 < new_qty <= product.low_stock:
                    stock_state = '3'
                elif new_qty <= 0:
                    stock_state = '2'
            location_ok = stock_locations_obj.search(
                [('product_id', '=', product_id),
                 ('location_id', '=', location)])
            if location_ok:
                if location_ok.qty != new_qty:
                    location_ok.write(
                        {'qty': new_qty,
                         'stock_state': stock_state})
                new_quants.append(location_ok.id)
            else:
                new_id = stock_locations_obj.create(
                    {'product_id': product_id,
                     'location_id': location,
                     'qty': new_qty,
                     'stock_state': stock_state})
                new_quants.append(new_id.id)
        self.product_stock_quants_ids = new_quants

    @api.one
    def _get_planned_dates(self):
        pol_obj = self.env['purchase.order.line']
        product_id = self.id
        pol_ids = pol_obj.search([('product_id', '=', product_id),
                                  ('state', 'in', ('draft', 'confirmed'))])
        self.product_planned_dates_ids = pol_ids

    product_stock_quants_ids = fields.One2many(
        compute=_get_locations_quants,
        comodel_name='location.quants',
        string='Locations Quants')
    product_planned_dates_ids = fields.One2many(
        compute=_get_planned_dates,
        comodel_name='purchase.order.line',
        string='Locations Quants')


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

    stock_alias = fields.Char('Alias Stock')
    website_published = fields.Boolean(
        'Available in the website',
        copy=False, default="_get_default_alias")

    @api.one
    def __get_default_alias(self):
        return self.name
