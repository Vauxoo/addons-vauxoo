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
        purchase_requisition_line_obj = self.pool.get(
            'purchase.requisition.line')
        item = len(res.keys())>=1 and res.keys()[0]  or False
        if item:
			purchase_requisition_line_ids = purchase_requisition_line_obj.search(
				cr, uid, [('requisition_id', '=', res.keys()[0])])
			order_line_obj = self.pool.get('purchase.order.line')
			purchase_requisition_lines = purchase_requisition_line_obj.browse(
				cr, uid, purchase_requisition_line_ids, context=context)
			for purchase_requisition_lines in purchase_requisition_lines:
				purchase_requisition_line_id = purchase_requisition_line_obj.search(cr, uid, [(
					'product_id', '=', int(purchase_requisition_lines.product_id.id)), ('requisition_id', '=', res.keys()[0]), 
					('product_qty','=', purchase_requisition_lines.product_qty) ])
				item_line_id = len(purchase_requisition_line_id)>=1 and purchase_requisition_line_id[0]  or False
				if item_line_id:
					name = purchase_requisition_line_obj.browse(
						cr, uid, purchase_requisition_line_id[0], context=context).name
					order_line_id_mod = order_line_obj.search(cr, uid, [('product_id', '=', int(
						purchase_requisition_lines.product_id.id)), ('order_id', '=', res.get(res.keys()[0], False)), ('product_qty','=', purchase_requisition_lines.product_qty)])
					order_line_obj.write(cr, uid, order_line_id_mod, {'name': name})
        return res
