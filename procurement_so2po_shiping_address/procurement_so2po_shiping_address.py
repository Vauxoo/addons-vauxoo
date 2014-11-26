# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Rodo(rodo@vauxoo.com)
#############################################################################
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
##########################################################################

from openerp.osv import fields, osv


class purchase_order(osv.Model):
    _inherit = 'purchase.order'

    _columns = {
        'partner_address_dest_id': fields.many2one('res.partner', 'Customer Address Dest',
            states={'confirmed': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]},
            help="Put an address if you want to deliver directly from the supplier to the customer. "
            "Otherwise, keep empty to deliver to your own company."
        ),
    }


class procurement_order(osv.Model):
    _inherit = 'procurement.order'

    def make_po(self, cr, uid, ids, context=None):
        purchase_obj = self.pool.get('purchase.order')
        res = super(procurement_order, self).make_po(cr, uid, ids=ids, context=context)
        for procurement in self.browse(cr, uid, ids, context=context):
            purchase_obj.write(cr, uid, res[procurement.id], {'partner_address_dest_id': procurement.partner_address_dest_id.id}, context=context)
        return res

    def _prepare_orderpoint_procurement(self, cr, uid, orderpoint, product_qty, context=None):
        res = super(procurement_order, self)._prepare_orderpoint_procurement(cr, uid, orderpoint=orderpoint, product_qty=product_qty, context=context)
        res['partner_address_dest_id'] = orderpoint.partner_shipping_id.id
        return res

    _columns = {
        'partner_address_dest_id': fields.many2one('res.partner', 'Customer Address Dest'),
    }


class sale_order(osv.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        res = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order=order, line=line, move_id=move_id, date_planned=date_planned, context=context)
        res['partner_address_dest_id'] = order.partner_shipping_id.id
        return res
