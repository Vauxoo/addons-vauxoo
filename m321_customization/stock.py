# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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


class inherited_stock(osv.Model):

    """
    M321 Customizations for product.picking model
    """

    _inherit = 'stock.picking'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        print "cr", cr

        res = super(inherited_stock, self).default_get(
            cr, uid, fields, context=context)
        #~ res.update({'total_sale':'noooo'})
        return res

    def _order_total(self, cr, uid, ids, name, arg, context=None):

        if context is None:
            context = {}

        if not len(ids):
            return {}
        res = {}
        picking_brw = self.browse(cr, uid, ids, context=context)
        if hasattr(picking_brw[0], "sale_id"):
            for picking in picking_brw:
                total = picking.sale_id and picking.sale_id.amount_total or 0
                res[picking.id] = total

        return res

    _columns = {
        'pay_state': fields.selection([
            ('paynot', 'Not Payed'),
            ('2bpay', 'To pay'),
            ('payed', 'Payed')], "Pay Control",
            help="The pay state for this picking"),
        'total_sale': fields.function(_order_total, method=True,
            type='float', string='Total Sale'),
        'sales_incoterm': fields.related('sale_id', 'incoterm',
            relation='stock.incoterms', type='many2one', string='Incoterm',
            readonly=True),
    }

    _defaults = {
        'pay_state': 'paynot',

    }

    def change_state(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_brw = self.browse(cr, uid, ids, context=context) and\
            self.browse(cr, uid, ids, context=context)[0]
        #~ print tuple([(i.product_id.name, i.product_qty) for i in picking_brw.move_lines if i.state != 'done' ])
        if all([False for i in picking_brw.move_lines if
                i.state == 'confirmed']):
            self.write(cr, uid, ids, {'pay_state': 'payed'}, context=context)
        else:
            e = '\n'.join(['The product %s with quantity %s is not available.'
                % (
                    i.product_id.name, i.product_qty)
                for i in picking_brw.move_lines if i.state == 'confirmed'])
            raise osv.except_osv(_(
                'Want to pay this without picking the availability\
                of these products?'), _(e))

        return True


class stock_move(osv.Model):

    _inherit = 'stock.move'
    _columns = {
        'id_sale': fields.many2one('sale.order', 'Sale Order'),
        'product_upc': fields.related('product_id', 'upc', type='char',
            string='UPC'),
        'product_ean13': fields.related('product_id', 'ean13', type='char',
            string='EAN13'),

    }
