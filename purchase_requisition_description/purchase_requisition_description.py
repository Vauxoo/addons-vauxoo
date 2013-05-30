# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.osv import fields, osv


class purchase_requisition_line (osv.Model):
    _inherit = "purchase.requisition.line"

    _columns = {
        'name': fields.text('Description', required=True),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, context=None):
        res = {'value': {}}
        dummy, name = self.pool.get('product.product').name_get(
            cr, uid, product_id, context=context)[0]
        product = self.pool.get('product.template').browse(
            cr, uid, product_id, context=context)
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})
        return res

purchase_requisition_line()


class purchase_requisition(osv.Model):
    _inherit = "purchase.requisition"

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        res = super(purchase_requisition, self).make_purchase_order(
            cr, uid, ids, partner_id, context=context)
        obj_purchase_requisition_line = self.pool.get(
            'purchase.requisition.line')
        purchase_requisition_line_ids = obj_purchase_requisition_line.search(
            cr, uid, [('requisition_id', '=', res.keys()[0])])
        obj_order_line = self.pool.get('purchase.order.line')
        obj_purchase_requisition_line_ = obj_purchase_requisition_line.browse(
            cr, uid, purchase_requisition_line_ids, context=context)
        for product_id in obj_purchase_requisition_line_:
            purchase_requisition_line_id = obj_purchase_requisition_line.search(cr, uid, [(
                'product_id', '=', int(product_id.product_id.id)), ('requisition_id', '=', res.keys()[0]), 
                ('product_qty','=', product_id.product_qty) ])
            name = obj_purchase_requisition_line.browse(
                cr, uid, purchase_requisition_line_id[0], context=context).name
            order_line_id_mod = obj_order_line.search(cr, uid, [('product_id', '=', int(
                product_id.product_id.id)), ('order_id', '=', res[res.keys()[0]]), ('product_qty','=', product_id.product_qty)])
            obj_order_line.write(cr, uid, order_line_id_mod, {'name': name})
        return res
