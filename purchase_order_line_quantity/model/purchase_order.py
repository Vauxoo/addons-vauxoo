# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


class PurchaseOrderLine(osv.osv):

    def _get_inv_quantity(self, cr, uid, ids, context=None):
        context = dict(context or {})
        res = 0.0
        ids = isinstance(ids, (int, long)) and [ids] or ids

        uom_obj = self.pool.get('product.uom')
        pol_brw = self.browse(cr, uid, ids[0], context=context)
        pol_uom_id = pol_brw.product_uom

        for ail_brw in pol_brw.invoice_lines:
            ail_uom_id = ail_brw.uos_id
            if ail_brw.invoice_id.state not in ('open', 'done'):
                continue
            if all([context.get('date_start'), context.get('date_stop')]):
                ai_brw = ail_brw.invoice_id
                if not (ai_brw.date_invoice >= context['date_start'] and
                        ai_brw.date_invoice <= context['date_stop']):
                    continue
            res += uom_obj._compute_qty_obj(cr, uid, ail_uom_id,
                                            ail_brw.quantity, pol_uom_id,
                                            context=context)

        return res

    def _get_move_quantity(self, cr, uid, ids, context=None):
        context = dict(context or {})
        res = 0.0
        ids = isinstance(ids, (int, long)) and [ids] or ids

        uom_obj = self.pool.get('product.uom')
        pol_brw = self.browse(cr, uid, ids[0], context=context)
        pol_uom_id = pol_brw.product_uom

        for sm_brw in pol_brw.move_ids:
            src = sm_brw.location_id.usage
            dst = sm_brw.location_dest_id.usage
            sm_uom_id = sm_brw.product_uom
            qty = 0.0
            if sm_brw.state != 'done':
                continue
            if all([context.get('date_start'), context.get('date_stop')]):
                if not (sm_brw.date >= context['date_start'] and
                        sm_brw.date <= context['date_stop']):
                    continue
            if src == dst:
                continue
            elif dst == 'internal':
                qty = uom_obj._compute_qty_obj(cr, uid, sm_uom_id,
                                               sm_brw.product_qty, pol_uom_id,
                                               context=context)
            elif src == 'internal':
                qty = -uom_obj._compute_qty_obj(cr, uid, sm_uom_id,
                                                sm_brw.product_qty, pol_uom_id,
                                                context=context)
            res += qty

        return res

    # def _get_ids_from_stock(self, cr, uid, ids, context=None):
    #     res = set([])
    #     sm_obj = self.pool.get('stock.move')
    #     for sm_brw in sm_obj.browse(cr, uid, ids, context=context):
    #         if not sm_brw.purchase_line_id:
    #             continue
    #         res.add(sm_brw.purchase_line_id.id)
    #     return list(res)

    # def _get_ids_from_invoice(self, cr, uid, ids, context=None):
    #     res = set([])
    #     ai_obj = self.pool.get('account.invoice')
    #     for ai_brw in ai_obj.browse(cr, uid, ids, context=context):
    #         if ai_brw.type not in ('in_invoice',):
    #             continue
    #         if ai_brw.state not in ('open', 'paid'):
    #             continue
    #         for ail_brw in ai_brw.invoice_line:
    #             if not ail_brw.purchase_line_id:
    #                 continue
    #             res.add(ail_brw.purchase_line_id.id)
    #     return list(res)

    def _get_quantity(self, cr, uid, ids, field_names=None, arg=False,
                      context=None):
        """ Finds quantity of product that has been delivered or invoiced.
        @return: Dictionary of values
        """
        field_names = field_names or []
        context = dict(context or {})
        res = {}
        for idx in ids:
            res[idx] = {}.fromkeys(field_names, 0.0)
        for fn in field_names:
            if fn == 'qty_delivered':
                for idx in ids:
                    res[idx][fn] = self._get_move_quantity(cr, uid, idx,
                                                           context=context)
            if fn == 'qty_invoiced':
                for idx in ids:
                    res[idx][fn] = self._get_inv_quantity(cr, uid, idx,
                                                          context=context)

        return res

    _inherit = 'purchase.order.line'
    _columns = {
        'qty_delivered': fields.function(
            _get_quantity,
            multi='qty',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity Delivered',
            help="Quantity Delivered"),
        'qty_invoiced': fields.function(
            _get_quantity,
            multi='qty',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity Invoiced',
            help="Quantity Invoiced"),
    }
