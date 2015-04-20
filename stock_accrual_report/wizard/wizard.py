# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
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

SELECTION_TYPE = [
    ('sale', 'Sale Order'),
    ('purchase', 'Purchase Order'),
]

SELECT_ORDER = [
    ('sale.order', 'Sale Order'),
    ('purchase.order', 'Purchase Order'),
]


SELECT_LINE = [
    ('sale.order.line', 'Sale Order Line'),
    ('purchase.order.line', 'Purchase Order Line'),
]


class stock_accrual_wizard_line(osv.osv_memory):
    _name = 'stock.accrual.wizard.line'
    _columns = {
        'wzd_id': fields.many2one(
            'stock.accrual.wizard',
            'Wizard'),
        'order_id': fields.reference(
            'Order',
            selection=SELECT_ORDER,
            size=128),
        'line_id': fields.reference(
            'Order Line',
            selection=SELECT_LINE,
            size=128),
        'product_qty': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Product UoS'),
        ),
        'product_uom': fields.many2one(
            'product.uom',
            'Unit of Measure ',
        ),
        'qty_delivered': fields.float(
            'Delivered Quantity',
            digits_compute=dp.get_precision('Product UoS'),
        ),
        'qty_invoiced': fields.float(
            'Invoiced Quantity',
            digits_compute=dp.get_precision('Product UoS'),
        ),
        'debit': fields.float(
            'Debit',
            digits_compute=dp.get_precision('Account')
        ),
        'credit': fields.float(
            'Credit',
            digits_compute=dp.get_precision('Account')
        ),
    }


class stock_accrual_wizard(osv.osv_memory):
    _name = 'stock.accrual.wizard'
    _rec_name = 'type'
    _columns = {
        'type': fields.selection(
            SELECTION_TYPE,
            string='Type',
            required=True
        ),
        'report_format': fields.selection([
            ('pdf', 'PDF'),
            ('xls', 'Spreadsheet')],
            'Report Format',
            required=True
        ),
        'line_ids': fields.one2many(
            'stock.accrual.wizard.line',
            'wzd_id',
            'Lines',
        )
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)

        self.compute_lines(cr, uid, ids, context.get('active_ids', []),
                           context=context)

        datas = {'active_ids': ids}
        context['active_ids'] = ids
        context['active_model'] = 'stock.accrual.wizard'

        context['xls_report'] = wzd_brw.report_format == 'xls'
        if wzd_brw.type == 'aging':
            name = None
        if wzd_brw.type == 'detail':
            name = None
        return self.pool['report'].get_action(cr, uid, [], name, data=datas,
                                              context=context)
