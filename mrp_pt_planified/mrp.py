# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
from openerp.tools.translate import _

from openerp.addons.decimal_precision import decimal_precision as dp


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'pt_planified_ids': [],
        })
        return super(mrp_production, self).copy(cr, uid, id, default, context)

    _columns = {
        'pt_planified_ids': fields.one2many('mrp.pt.planified',
            'production_id', 'Products Finished Good Planified'),
    }

    def action_compute(self, cr, uid, ids, properties=[], context=None):
        mrp_pt = self.pool.get('mrp.pt.planified')
        bom_obj = self.pool.get('mrp.bom')
        for production in self.browse(cr, uid, ids, context=context):

            mrp_pt.unlink(cr, uid, map(
                lambda x: x.id, production.pt_planified_ids))

            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(
                    cr, uid, production.product_id.id,
                    production.product_uom.id, properties)

            if not bom_id:
                raise osv.except_osv(_('Error'), _(
                    "Couldn't find a bill of material for this product."))

            for pro in bom_obj.browse(cr, uid, [bom_id]):
                val = {
                    'product_id': pro.product_id and
                    pro.product_id.id or False,
                    'quantity': production.product_qty,
                    'product_uom': production.product_uom.id,
                    'production_id': production.id
                }
                mrp_pt.create(cr, uid, val)
        res = super(mrp_production, self).action_compute(
            cr, uid, ids, properties=properties, context=context)
        return res


class mrp_pt_planified(osv.Model):
    _name = 'mrp.pt.planified'
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product',
            required=True),
        'quantity': fields.float('quantity',
            digits_compute=dp.get_precision('Product UoM'), required=True),
        'production_id': fields.many2one('mrp.production', 'production'),
        'product_uom': fields.many2one('product.uom', 'UoM', required=True)
    }

    def on_change_product_uom(self, cr, uid, ids, product_id):
        product_product = self.pool.get('product.product')
        if product_id:
            product = product_product.browse(cr, uid, product_id)
            return {'value': {'product_uom': product.uom_id and
                              product.uom_id.id}}
        return {'value': {'product_uom': False}}
