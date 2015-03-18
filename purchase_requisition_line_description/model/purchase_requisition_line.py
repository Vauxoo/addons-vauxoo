# -*- encoding: utf-8 -*-
########################################################################
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
########################################################################

from openerp.osv import fields, osv


class purchase_requisition_line(osv.Model):
    _inherit = "purchase.requisition.line"

    _columns = {
        'name': fields.char('Description', size=256),
    }

    def init(self, cr):
        cr.execute("""UPDATE purchase_requisition_line prl
                      SET name = (SELECT CONCAT('[',default_code,']',' ', name_template )
                                  FROM product_product pp
                                  WHERE pp.id = prl.product_id)
                                  WHERE prl.name is NULL""")

    def onchange_product_id(self, cr, uid, ids, product_id,
                            product_uom_id, context=None):
        context = context or {}
        product_obj = self.pool.get('product.product')
        res = super(purchase_requisition_line, self).onchange_product_id(
            cr, uid, ids, product_id, product_uom_id, context=context)
        res['value'].update({'name': ''})
        if product_id:
            product_name = product_obj.name_get(
                cr, uid, product_id, context=context)
            dummy, name = product_name and product_name[0] or (False,
                                                               False)

            product = product_obj.browse(cr, uid, product_id,
                                         context=context)
            if product.description_purchase:
                name += '\n' + product.description_purchase
            res['value'].update({'name': name})
        return res

purchase_requisition_line()


class purchase_requisition(osv.Model):
    _inherit = "purchase.requisition"

    def make_purchase_order(self, cr, uid, ids, partner_id,
                            context=None):
        if context is None:
            context = {}
        res = super(purchase_requisition, self).make_purchase_order(cr, uid, ids, partner_id, context=context)

        pol_obj = self.pool.get('purchase.order.line')
        po_obj = self.pool.get('purchase.order')

        for requisition in self.browse(cr, uid, ids, context=context):
            po_req = po_obj.search(cr, uid, [('requisition_id', '=', requisition.id)], context=context)
            for po_id in po_req:
                pol_ids = pol_obj.search(cr, uid, [('order_id', '=', po_id)])
                for pol_id in pol_ids:
                    pol_brw = pol_obj.browse(cr, uid, pol_id)
                    pol_obj.write(cr, uid, [pol_brw.id], {'name':
                        pol_brw.purchase_requisition_line_id.name}, context=context)
        return res
