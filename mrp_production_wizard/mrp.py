# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

from openerp.tools.translate import _

from openerp.osv import osv
import time


class mrp_production(osv.Model):
    _inherit = "mrp.production"

    """
    """
    def create_production_wizard(self, cr, uid, product, list_produce,
                                    context):
        """ creates the production order
        @param product id to create
        @return: True
        """

        total_weight = 0
        for line in list_produce:
                product_obj_data = self.pool.get('product.product').browse(
                    cr, uid, line['product_id'], context=None)
                if product_obj_data.weight:
                    total_weight += (line['product_qty'] *\
                        product_obj_data.weight * (product.uom_id.factor /\
                        product_obj_data.uom_id.factor))
                else:
                    total_weight += line['product_qty'] * (
                        product.uom_id.factor / product_obj_data.uom_id.factor)
        total_weight = total_weight / ((
            product.weight or 1) * product.uom_id.factor)

        default_location_dict = self.product_id_change(
            cr, uid, [], product.id, context)
        if (default_location_dict['value']['location_src_id'] &\
        default_location_dict['value']['location_dest_id']):
            production_order_dict = {
                'name': self.pool.get('ir.sequence').get(cr, uid, 
                        'mrp.production'),
                'date_planned': time.strftime('%Y-%m-%d %H:%M:%S'),
                'product_id': product.id,
                'product_qty': total_weight,
                'product_uom': product.uom_id.id,
                'location_src_id': default_location_dict['value']['location_src_id'],
                'location_dest_id': default_location_dict['value']['location_dest_id'],
                'state': 'draft'
            }
            new_id = self.create(cr, uid, production_order_dict)

            for line in list_produce:
                production_scheduled_dict = {
                    'name': line['name'],
                    'product_id': line['product_id'],
                    'product_qty': line['product_qty'],
                    'product_uom': line['product_uom'],
                    'production_id': new_id,
                }
                self.pool.get('mrp.production.product.line').create(
                    cr, uid, production_scheduled_dict)

            mrp_pt_planifed_dict = {
                'product_id': product.id,
                'quantity': total_weight,
                'production_id': new_id,
                'product_uom': product.uom_id.id,
            }
            self.pool.get('mrp.pt.planified').create(
                cr, uid, mrp_pt_planifed_dict)
        else:
            raise osv.except_osv(_('Error'), _(
                "The category of the product to produce has not\
                predefined locations "))
        return new_id
