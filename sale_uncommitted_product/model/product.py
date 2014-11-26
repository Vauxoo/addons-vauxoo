# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
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
##########################################################################


from openerp.osv import osv, fields

from openerp.addons.decimal_precision import decimal_precision as dp


class product_product(osv.Model):
    _inherit = "product.product"

    def _get_product_committed_amount(self, cr, uid, ids, context=None):
        amount = 0.0
        sol_obj = self.pool.get('sale.order.line')
        uom_obj = self.pool.get('product.uom')
        for sol_brw in sol_obj.browse(cr, uid, ids, context=context):
            from_uom_id = sol_brw.product_uom
            to_uom_id = sol_brw.product_id.uom_id
            qty = sol_brw.product_uom_qty
            amount += uom_obj._compute_qty_obj(
                cr, uid, from_uom_id, qty, to_uom_id, context=context)
        return amount

    def _product_committed(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        """ Finds the committed products where are on
        committed sale orders.
        @return: Dictionary of values
        """

        sol_obj = self.pool.get('sale.order.line')

        if not field_names:
            field_names = []
        if context is None:
            context = {}

        res = {}

        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)

        for id in ids:
            #~ TODO: Cambiar por una sentencia sql para
            # no tener que pasar el usuario 1
            sol_ids = sol_obj.search(cr, 1, [('order_id', '!=', False),
                                             ('order_id.state', '=',
                                              'committed'),
                                             ('product_id', '=', id)],
                                     context=context)

            amount = 0.0
            if sol_ids and field_names:
                amount = self._get_product_committed_amount(
                    cr, uid, sol_ids, context=context)

            for f in field_names:
                if f == 'qty_committed':
                    res[id][f] = amount
                elif f == 'qty_uncommitted':
                    prd_brw = self.browse(cr, uid, id, context=context)
                    res[id][f] = prd_brw.qty_available + \
                        prd_brw.outgoing_qty - amount
        return res

    _columns = {
        'qty_committed': fields.function(_product_committed, method=True,
                                         type='float', string='Sale Committed',
                                         multi='committed',
                                         help="""Current quantities of
                                                 committed products in
                                                 Committe Sale Orders.""",
                                         digits_compute=dp.get_precision('Product UoM')),
        'qty_uncommitted': fields.function(_product_committed, method=True,
                                           type='float', string='Uncommitted',
                                           multi='committed',
                                           help="""Current quantities of
                                                   committed products in
                                                   Committe Sale Orders.i""",
                                           digits_compute=dp.get_precision('Product UoM')),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
