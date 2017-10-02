# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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
#
from openerp.osv import osv, fields


class SaleOrderLine(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'sequence2': fields.related(
            'sequence', type='integer', relation='sale.order.line',
            string='Sequence',
            help='Field to show the number of sequence in line')
    }

    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):

        context = context or {}

        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position, flag=flag,
            context=context)

        if product:
            product_id = self.pool.get('product.product').browse(
                cr, uid, product, context=context)
            prod_category = product_id.categ_id and product_id.categ_id.name
            name_description = res.get('value', {}).pop('name', '')
            if not name_description:
                return res
            name_description = '[%s]' % (prod_category) + name_description
            res.get('value', {}).update({'name': name_description})
        return res


class SaleOrder(osv.osv):

    _inherit = 'sale.order'

    def create(self, cr, uid, values, context=None):

        new_id = super(SaleOrder, self).create(
            cr, uid, values, context=context)

        if values.get('order_line'):
            self._get_order_line_categ(cr, uid, new_id, context=context)

        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        res = super(SaleOrder, self).write(
            cr, uid, ids, vals, context=context)

        if 'order_line' in vals:
            self._get_order_line_categ(cr, uid, ids, context=context)

        return res

    def _get_order_line_categ(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        for order_id in ids:
            cr.execute("""
                UPDATE sale_order_line SET sequence=sq.rownumber
                FROM (SELECT ROW_NUMBER() OVER(ORDER BY name) AS RowNumber, id
                      FROM sale_order_line WHERE order_id=%s) sq
                WHERE sq.id=sale_order_line.id
            """, (order_id,))
        return True
