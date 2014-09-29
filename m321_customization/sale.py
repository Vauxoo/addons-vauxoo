# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Luis Escobar  <p.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _



class inherited_sale_order(osv.Model):
    _inherit = "sale.order"

    def default_get(self, cr, uid, fields, context=None):
        """
             To get default values for the object.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param fields: List of fields for which we want default values
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        res = super(inherited_sale_order, self).default_get(
            cr, uid, fields, context=context)
        res.get('order_policy', False) and res.update(
            {'order_policy': 'picking'})
        return res

    _defaults = {
        'order_policy': 'picking'
    }

    def qty_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        product = []
        sale_brw = ids and self.browse(cr, uid, ids[0], context=context)
        for line in sale_brw.order_line:
            virtual = line.product_id.qty_available
            real = line.product_id.virtual_available
            if virtual == real and\
                line.product_uom_qty > virtual or\
                line.product_uom_qty > virtual:
                raise osv.except_osv(_('Error'), _(
                    'The quantity in the line of the product %s is minor that\
                    quantity available ' % line.product_id.name))

            elif virtual > real and line.product_uom_qty > real and\
                line.product_uom_qty < virtual and not line.check_confirm:
                raise osv.except_osv(_('Error'), _(
                    'The amount you want to sell is not available in the real\
                    stock of product %s, but if a shipment next, if you want\
                    to make this sale select Stock future sales line'
                    % line.product_id.name))

        return True


class sale_order_line(osv.Model):

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                            uom=False, qty_uos=0, uos=False, name='',
                            partner_id=False,
                            lang=False, update_tax=True, date_order=False,
                            packaging=False, fiscal_position=False, flag=False,
                            context=None):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        res = super(
            sale_order_line, self).product_id_change(cr, uid, ids, pricelist,
                                 product, qty=qty,
                                 uom=uom, qty_uos=qty_uos,
                                 uos=uos, name=name,
                                 partner_id=partner_id,
                                 lang=lang,
                                 update_tax=update_tax,
                                 date_order=date_order,
                                 packaging=packaging,
                                 fiscal_position=fiscal_position, flag=flag)

        future_stock = product and self.pool.get(
            'stock.move').search(cr, uid, [('product_id', '=', product),
                           ('state', 'in', (
                            'assigned', 'confirmed', 'waiting')),
                           ('picking_id.type', '=', 'in')], context=context)
        future_stock and res.get('value', False) and res.get(
            'value', False).update({'stock_move_ids': future_stock})

        return res

    _inherit = 'sale.order.line'
    _columns = {
        'stock_move_ids': fields.one2many('stock.move', 'id_sale',
            'Future Stock', readonly=True,
            help="Stock move future to reference of salesman for knowing that\
                product is available"),
        'check_confirm': fields.boolean("Future Stock'",
            help="This field indicates if the salesman is in accordance with\
                sale a product   that is not available but if in a\
                future stock"),

    }
