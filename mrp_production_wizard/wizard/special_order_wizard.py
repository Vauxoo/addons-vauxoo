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
import time
from openerp.osv import osv, fields
import decimal_precision as dp
from openerp.tools.translate import _


class mrp_production_wizard(osv.TransientModel):
    _name = 'mrp.production.wizard'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product',
            required=True, ),
        #'product_qty': fields.float('Product Qty', required=True),
        #'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'wiz_data': fields.one2many('wizard.data', 'mrp_production_wiz',
            'Prod lines'),
    }

    def pass_products_to_parent(self, cr, uid, ids, context={}):
        if not context:
            context = {}
        wizard_data_data = self.browse(cr, uid, ids, context=context)
        list_product_lines = []
        dict_line = {}
        for line in wizard_data_data:
            product = line.product_id
            for move in line.wiz_data:
                dict_line = {
                    'name': move.name,
                    'product_id': move.product_id_consume.id,
                    'product_qty': move.product_qty,
                    'product_uom': move.product_uom.id}
                list_product_lines.append(dict_line)
        mrp_production_id = self.pool.get('mrp.production').create_production_wizard(
            cr, uid, product, list_product_lines, context=context)

        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(
            cr, uid, 'mrp', 'mrp_production_form_view')
        res_id = res and res[1] or False,
        return {
            'name': _('Manufacturing orders'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'mrp.production',
            'context': "",
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': mrp_production_id or False,
        }

    # def onchange_product_to_produce(self, cr, uid, ids, product_id):
    #    res = self.pool.get('wizard.data').onchange_production_wizard_product_name(cr, uid, ids, product_id)
    #    print res['value'], " = res value"
    #    return res


class wizard_data(osv.TransientModel):
    _name = 'wizard.data'

    _columns = {
        'mrp_production_wiz': fields.many2one('mrp.production.wizard',
            'Padre'),
        'name': fields.char('Name', size=64, required=True),
        'product_id_consume': fields.many2one('product.product', 'Product',
            required=True),
        'product_qty': fields.float('Product Qty', required=True),
        'product_uom': fields.many2one('product.uom', 'Product UOM',
            required=True),
    }

    def onchange_production_wizard_product_name(self, cr, uid, ids,
                                                product_id):
        if product_id:
            new_product_id = [product_id]
            product_product_obj = self.pool.get('product.product')
            product_product_data = product_product_obj.browse(
                cr, uid, new_product_id, context=None)
            if product_product_data:
                for line in product_product_data:
                    val = {
                        'name': line.name,
                        'product_uom': line.uom_id.id,
                        'product_qty': line.qty_available,
                    }
                    domain_uom = {'product_uom': [(
                        'category_id', '=', line.uom_id.category_id.id)]}
                    return {'value': val, 'domain': domain_uom}
        return {}
