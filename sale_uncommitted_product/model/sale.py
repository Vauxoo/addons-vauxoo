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
from openerp.tools.translate import _

import time


class sale_order(osv.Model):
    _inherit = "sale.order"

    _columns = {
        'date_committed': fields.datetime('Commitment Date',
                                          help='''Date when Sale Order was
                                                   committed to the
                                                   Customer''',
                                          readonly=True),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('committed', 'Committed'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Order State', readonly=True,
            help="""Gives the state of the quotation or sales order. \n
                The exception state is automatically set when a cancel
                operation occurs in the invoice validation (Invoice Exception)
                or in the picking list process (Shipping Exception). \n
                The 'Waiting Schedule' state is set when the invoice is
                confirmed but waiting for the scheduler to run on the date
                'Ordered Date'.""", select=True),
    }

    def action_commit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'committed',
                   'date_committed': time.strftime(
                                  '%Y-%m-%d %H:%M:%S')}, context=context)
        return True

    def _check_so(self, cr, uid, id, context=None):
        if context is None:
            context = {}

        uom_obj = self.pool.get('product.uom')
        pp_obj = self.pool.get('product.product')

        note = '\n'
        check = True
        res = {}
        for sol_brw in self.browse(cr, uid, id, context=context).order_line:
            if sol_brw.product_id and sol_brw.product_id.type != "service":
                from_uom_id = sol_brw.product_uom
                to_uom_id = sol_brw.product_id.uom_id
                qty = sol_brw.product_uom_qty
                amount = uom_obj._compute_qty_obj(
                    cr, uid, from_uom_id, qty, to_uom_id, context=context)
                if res.get(sol_brw.product_id.id):
                    res[sol_brw.product_id.id] += amount
                else:
                    res[sol_brw.product_id.id] = amount
        for p_id in res:
            pp_brw = pp_obj.browse(cr, uid, p_id, context=context)
            if res[p_id] > pp_brw.qty_uncommitted:
                check = False
                note += _('\n[%s] %s - requested: %s, available: %s') % (
                    pp_brw.default_code or 'N/D',
                    pp_brw.name, res[p_id], pp_brw.qty_uncommitted)

        return {'note': note, 'check': check}

    def check_committed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for id in ids:
            res = self._check_so(cr, uid, id, context=context)
            if not res['check']:
                note = _('''Sale Order No.: %s\nHas exceeded the
                            uncommited quantity for:\n''') % (
                    self.browse(cr, uid, id, context=context).name)
                raise osv.except_osv(_(
                    'Exceeded Committed Products in Sale Order'),
                    note + res['note'])
        return True
