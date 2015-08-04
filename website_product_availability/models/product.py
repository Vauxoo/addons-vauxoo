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
from openerp.osv import osv, fields


class stock_location_route(osv.Model):
    _inherit = 'stock.location.route'
    _columns = {
        'consider_on_request': fields.boolean('Route On Request',
                                              help="Checking this you will\
                                              consider this route as an \
                                              'On Request' route, this means\
                                              that every product that has this\
                                              route assigned will show on the\
                                              website the legend 'On Request'\
                                              on the availability field,\
                                              please be careful to set up this\
                                              route."),
    }


class product_product(osv.Model):
    _inherit = 'product.product'
    SELECTION_LIST = [
        ('1', 'Available'),
        ('2', 'Not Available'),
        ('3', 'Low Availability'),
        ('4', 'On Request'),
    ]

    def _get_availability(self, cr, uid, ids, name, args, context=None):
        res = {}
        for product in self.browse(cr, uid, ids):
            for route in product.route_ids:
                if route.consider_on_request:
                    res[product.id] = '4'
                    return res
            if product.qty_available > product.low_stock:
                res[product.id] = '1'
                return res
            elif 0 < product.qty_available <= product.low_stock:
                res[product.id] = '3'
                return res
            elif product.qty_available <= 0:
                res[product.id] = '2'
                return res

    _columns = {
        'low_stock': fields.integer('Low Stock', help="This field is used to show\
    on the website when a product has low availability, any number of stock\
    equals the value set or lower will show 'low avilability' on product "),
        'stock_state': fields.function(_get_availability, type='selection',
                                       method=True, selection=SELECTION_LIST,
                                       string="Website Stock State",
                                       store=True),
    }
    _default = {
        'low_stock': 0,
    }


class LocationQuants(osv.Model):
    _name = 'location.quants'

    _columns = {
        'product_id': fields.many2one('product.template'),
        'location_id': fields.many2one('stock.location'),
        'qty': fields.float()
    }


class ProductTemplate(osv.Model):
    _inherit = 'product.template'

    def _get_locations_quants(
            self, cr, uid, ids, field_names, arg=None, context=None):
        stock_locations_obj = self.pool.get('location.quants')
        stock_quants_obj = self.pool.get('stock.quant')
        res = {}
        for product_id in ids:
            products = self._get_products(cr, uid, product_id, context=context)
            quants = stock_quants_obj.search(
                cr, uid,
                [('product_id', 'in', products),
                 ('location_id.usage', '=', 'internal')])
            stock_locations_ids = []
            for quant in stock_quants_obj.browse(
                    cr, uid, quants, context=context):
                if quant.location_id.id in stock_locations_ids:
                    continue
                stock_locations_ids.append(quant.location_id.id)

            location_quant_ids = stock_locations_obj.search(
                cr, uid, [('product_id', 'in', products),
                          ('location_id', 'in', stock_locations_ids)],
                context=context)

            if location_quant_ids:
                stock_locations_obj.unlink(
                    cr, uid, location_quant_ids, context=context)
            ctx = dict(context)
            new_quants = []
            for location in stock_locations_ids:
                ctx['location'] = location
                qtys = self._product_available(
                    cr, uid, ids, field_names, arg, context=ctx)
                new_id = stock_locations_obj.create(
                    cr, uid,
                    {'product_id': product_id,
                     'location_id': location,
                     'qty': qtys.get(ids[0]).get('qty_available')})
                new_quants.append(new_id)

            res[product_id] = new_quants
        return res

    def _get_planned_dates(
            self, cr, uid, ids, field_names, arg=None, context=None):
        pol_obj = self.pool.get('purchase.order.line')
        res = {}
        for product_id in ids:
            products = self._get_products(cr, uid, ids, context=context)
            pol_ids = pol_obj.search(
                cr, uid, [('product_id', 'in', products),
                          ('state', 'in', ('draft', 'confirmed'))],
                context=context)
            res[product_id] = pol_ids
        return res

    _columns = {
        'product_stock_quants_ids': fields.function(
            _get_locations_quants,
            relation='location.quants',
            type='one2many',
            string='Locations Quants'),
        'product_planned_dates_ids': fields.function(
            _get_planned_dates,
            relation='purchase.order.line',
            type='one2many',
            string='Locations Quants'), }
