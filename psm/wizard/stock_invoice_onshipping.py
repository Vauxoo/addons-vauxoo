# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


class stock_invoice_onshipping_psm(osv.TransientModel):

    _inherit = "stock.invoice.onshipping"

    _columns = {
        'group_by_product': fields.boolean("Group by product"),
    }

    _defaults = {
        'group_by_product': True,
    }

    def drop_duplicate_invoice_lines(self, cr, uid, invoice_id, product_ids, context=None):
        if context is None:
            context = {}
        ail = self.pool.get('account.invoice.line')
        for prod_id in product_ids:
            quantity = 0.0
            price_subtotal = 0.0
            ail_search = ail.search(cr, uid, [(
                'invoice_id', '=', invoice_id), ('product_id', '=', prod_id)])
            if len(ail_search) > 1:
                ail_brw = ail.browse(cr, uid, ail_search, context=context)
                for ail_aux in ail_brw:
                    price_subtotal += ail_aux.price_subtotal
                    quantity += ail_aux.quantity
                value = {
                    'price_subtotal': price_subtotal,
                    'quantity': quantity
                }
                ail.write(cr, uid, [ail_brw[0].id], value, context=context)
                ail.unlink(cr, uid, [x.id for x in ail_brw[1:]])

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        prod = []
        res = super(stock_invoice_onshipping_psm, self).create_invoice(
            cr, uid, ids, context=context)
        onshipdata_obj = self.read(cr, uid, ids, ['group_by_product'])[0]
        if onshipdata_obj.get('group_by_product'):
            acc_invoice = self.pool.get("account.invoice")
            for r in res:
                invoice = acc_invoice.browse(
                    cr, uid, [res[r]], context=context)[0]
                invoice_lines = invoice.invoice_line
                for invoice_line in invoice_lines:
                    prod.append(invoice_line.product_id.id)
                self.drop_duplicate_invoice_lines(
                    cr, uid, invoice.id, list(set(prod)), context=context)
        return res
