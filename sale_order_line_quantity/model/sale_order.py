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


class SaleOrderLine(osv.osv):

    def _get_inv_quantity(self, cr, uid, ids, context=None):
        context = dict(context or {})
        res = 0.0
        ids = isinstance(ids, (int, long)) and [ids] or ids

        uom_obj = self.pool.get('product.uom')
        sol_brw = self.browse(cr, uid, ids[0], context=context)
        sol_uom_id = sol_brw.product_uom

        for ail_brw in sol_brw.invoice_lines:
            ail_uom_id = ail_brw.uos_id
            if ail_brw.invoice_id.state not in ('open', 'done'):
                continue
            if all([context.get('date_start'), context.get('date_stop')]):
                ai_brw = ail_brw.invoice_id
                if not (ai_brw.date_invoice >= context['date_start'] and
                        ai_brw.date_invoice <= context['date_stop']):
                    continue
            res += uom_obj._compute_qty_obj(cr, uid, ail_uom_id,
                                            ail_brw.quantity, sol_uom_id,
                                            context=context)

        return res

    def _get_move_quantity(self, cr, uid, ids, context=None):
        context = dict(context or {})
        res = 0.0
        ids = isinstance(ids, (int, long)) and [ids] or ids

        uom_obj = self.pool.get('product.uom')
        sol_brw = self.browse(cr, uid, ids[0], context=context)
        sol_uom_id = sol_brw.product_uom

        for sm_brw in sol_brw.move_ids:
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
            elif src == 'internal':
                qty = uom_obj._compute_qty_obj(cr, uid, sm_uom_id,
                                               sm_brw.product_qty, sol_uom_id,
                                               context=context)
            elif dst == 'internal':
                qty = -uom_obj._compute_qty_obj(cr, uid, sm_uom_id,
                                                sm_brw.product_qty, sol_uom_id,
                                                context=context)
            res += qty

        return res

    def _get_qty_delivered(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        """ Finds quantity of product that has been delivered.
        @return: Dictionary of values
        """
        context = dict(context or {})
        res = {}.fromkeys(ids, 0.0)
        for idx in ids:
            res[idx] = self._get_move_quantity(cr, uid, idx, context=context)

        return res

    # def _get_ids_from_stock(self, cr, uid, ids, context=None):
    #     res = set([])
    #     sm_obj = self.pool.get('stock.move')
    #     for sm_brw in sm_obj.browse(cr, uid, ids, context=context):
    #         if not sm_brw.sale_line_id:
    #             continue
    #         res.add(sm_brw.sale_line_id.id)
    #     return list(res)

    def _get_qty_invoiced(self, cr, uid, ids, field_names=None, arg=False,
                          context=None):
        """ Finds quantity of product that has been invoiced.
        @return: Dictionary of values
        """
        context = dict(context or {})
        res = {}.fromkeys(ids, 0.0)
        for idx in ids:
            res[idx] = self._get_inv_quantity(cr, uid, idx, context=context)
        return res

    # def _get_ids_from_invoice(self, cr, uid, ids, context=None):
    #     res = set([])
    #     ai_obj = self.pool.get('account.invoice')
    #     for ai_brw in ai_obj.browse(cr, uid, ids, context=context):
    #         if ai_brw.type not in ('out_invoice',):
    #             continue
    #         if ai_brw.state not in ('open', 'paid'):
    #             continue
    #         for ail_brw in ai_brw.invoice_line:
    #             if not ail_brw.sale_line_id:
    #                 continue
    #             res.add(ail_brw.sale_line_id.id)
    #     return list(res)

    _inherit = 'sale.order.line'
    _columns = {
        'qty_delivered': fields.function(
            _get_qty_delivered,
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity Delivered',
            # store={
            #     'stock.move': (_get_ids_from_stock, ['state'], 15),
            # },
            help="Quantity Delivered"),
        'qty_invoiced': fields.function(
            _get_qty_invoiced,
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity Invoiced',
            # store={
            #     'account.invoice': (_get_ids_from_invoice, ['state'], 15),
            # },
            help="Quantity Invoiced"),
    }
