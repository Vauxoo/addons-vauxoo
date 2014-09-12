# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp
import time
from openerp.tools.translate import _


class wizard_production_make(osv.TransientModel):
    _name = 'wizard.production.make'

    _columns = {
        'products_ids': fields.many2many('product.product', 'production_make',
            'product_id', 'production_make_id', 'Products'),
        'date_planned': fields.datetime('Scheduled date', required=True,
            select=1),
        'location_src_id': fields.many2one('stock.location',
            'Raw Materials Location', readonly=False,
            help="Location where the system will look for components."),
        'location_dest_id': fields.many2one('stock.location',
            'Finished Products Location', readonly=False,
            help="Location where the system will stock the\
                finished products."),
    }
    _defaults = {
        'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def action_add_production(self, cr, uid, ids, context=None):
        production_obj = self.pool.get('mrp.production')
        product_obj = self.pool.get('product.product')
        wiz_product = self.browse(cr, uid, ids, context=context)
        list_orders = []
        for products in wiz_product:
            for product in products.products_ids:
                data_product = product_obj.browse(
                    cr, uid, product.id, context=context).uom_id.id
                if not product.categ_id.location_src_id.id and not\
                products.location_src_id.id:
                    raise osv.except_osv(_('Error!'), _(
                        "Not set a location of raw material for the product: "
                        +product.name))
                if not product.categ_id.location_dest_id.id and not\
                products.location_dest_id.id:
                    raise osv.except_osv(_('Error!'), _(
                        "Not set a location of finished products for the\
                        product: "+product.name))
                location_src = product.categ_id.location_src_id.id or\
                                products.location_src_id.id
                location_dest = product.categ_id.location_dest_id.id or\
                                products.location_dest_id.id
                production_id = production_obj.create(cr, uid, {
                    'product_id': product.id,
                    'product_qty': '1.0',
                    'product_uom': data_product,
                    'date_planned': products.date_planned,
                    'location_src_id': location_src,
                    'location_dest_id': location_dest,
                })
                list_orders.append(production_id)
        return {
            'name': 'Customer Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', list_orders)],
        }
