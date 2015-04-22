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
from openerp.tools.translate import _

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

SALE_STATES = [
    'waiting_date',
    'progress',
    'manual',
    'shipping_except',
    'invoice_except',
    'done',
]

PURCHASE_STATES = [
    'approved',
    'except_picking',
    'except_invoice',
    'done',
]

QUERY = '''
SELECT order_id
FROM {ttype}_order_line AS ol
INNER JOIN
    {ttype}_order_line_invoice_rel AS olir ON olir.order_line_id = ol.order_id
INNER JOIN
    account_invoice_line AS ail ON ail.id = olir.invoice_id
INNER JOIN
    account_invoice AS ai ON ai.id = ail.invoice_id
INNER JOIN
    res_company AS rc on rc.id = ai.company_id
WHERE
    ai.state IN ('open', 'paid')
    AND (ai.date_invoice BETWEEN '{date_start}' AND '{date_stop}')
    AND rc.id = {company_id}
'''


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

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid,
                                                             context=context)
        if not company_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is no default company for the current user!'))
        return company_id

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
        'period_id': fields.many2one(
            'account.period',
            domain="[('special','=',False)]",
            string='Period',
            required=True,
        ),
        'line_ids': fields.one2many(
            'stock.accrual.wizard.line',
            'wzd_id',
            'Lines',
        ),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True),
        'user_id': fields.many2one(
            'res.users',
            'User'),
    }

    _defaults = {
        'report_format': lambda *args: 'pdf',
        'type': lambda *args: 'sale',
        'company_id': _get_default_company,
        'user_id': lambda s, c, u, cx: s.pool.get('res.users').browse(c, u, u,
                                                                      cx).id,
    }

    def _get_accrual(self, cr, uid, ids, line_brw, context=None):
        context = context or {}
        res = {'debit': 0.0, 'credit': 0.0}
        for move in line_brw.move_ids:
            for aml_brw in move.aml_ids:
                if not aml_brw.account_id.reconcile:
                    continue
                res['debit'] += aml_brw.debit
                res['credit'] += aml_brw.credit
        return res

    def _get_lines(self, cr, uid, wzd_brw, order_brw, line_brw, context=None):
        context = context or {}
        if 'sale' in order_brw._name:
            product_qty = line_brw.product_uom_qty
        if 'purchase' in order_brw._name:
            product_qty = line_brw.product_qty
        res = {
            'wzd_id': wzd_brw.id,
            'order_id': '%s,%s' % (order_brw._name, order_brw.id),
            'line_id': '%s,%s' % (line_brw._name, line_brw.id),
            'product_qty': product_qty,
            'product_uom': line_brw.product_uom.id,
            'qty_delivered': line_brw.qty_delivered,
            'qty_invoiced': line_brw.qty_invoiced,
        }
        res.update(self._get_accrual(cr, uid, wzd_brw.id, line_brw,
                                     context=context))
        return res

    def _get_records_from_invoice(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        ttype = 'sale' if wzd_brw.type == 'sale' else 'purchase'
        query = QUERY.format(
            ttype=ttype,
            company_id=wzd_brw.company_id.id,
            date_start=wzd_brw.period_id.date_start,
            date_stop=wzd_brw.period_id.date_stop,
        )
        cr.execute(query)
        res = cr.fetchall()
        return set(res)

    def compute_purchase_lines(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        sm_obj = self.pool.get('stock.move')
        purchase_obj = self.pool.get('purchase.order')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        date_start = wzd_brw.period_id.date_start
        date_stop = wzd_brw.period_id.date_stop
        sm_ids = sm_obj.search(cr, uid, [
            ('state', '=', 'done'),
            ('date', '>=', date_start),
            ('date', '<=', date_stop),
            ('purchase_line_id', '!=', False)],
            context=context)
        record_ids = set([])
        for sm_brw in sm_obj.browse(cr, uid, sm_ids, context=context):
            record_ids.add(sm_brw.purchase_line_id.order_id.id)
        res = []
        record_brws = []
        if record_ids:
            record_brws = purchase_obj.browse(cr, uid, record_ids,
                                              context=context)
        record_idx = self._get_records_from_invoice(cr, uid, ids,
                                                    context=context)
        record_ids = record_ids | record_idx
        for record_brw in record_brws:
            for line_brw in record_brw.order_line:
                res.append(self._get_lines(cr, uid, wzd_brw, record_brw,
                                           line_brw, context=context))
        return res

    def compute_sale_lines(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        sm_obj = self.pool.get('stock.move')
        sale_obj = self.pool.get('sale.order')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        date_start = wzd_brw.period_id.date_start
        date_stop = wzd_brw.period_id.date_stop
        sm_ids = sm_obj.search(cr, uid, [
            ('state', '=', 'done'),
            ('date', '>=', date_start),
            ('date', '<=', date_stop),
            ('sale_line_id', '!=', False)],
            context=context)
        record_ids = set([])
        for sm_brw in sm_obj.browse(cr, uid, sm_ids, context=context):
            record_ids.add(sm_brw.sale_line_id.order_id.id)
        record_idx = self._get_records_from_invoice(cr, uid, ids,
                                                    context=context)
        record_ids = record_ids | record_idx
        res = []
        record_brws = []
        if record_ids:
            record_ids = list(record_ids)
            record_brws = sale_obj.browse(cr, uid, record_ids, context=context)
        for record_brw in record_brws:
            for line_brw in record_brw.order_line:
                res.append(self._get_lines(cr, uid, wzd_brw, record_brw,
                                           line_brw, context=context))
        return res

    def compute_lines(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        sawl_obj = self.pool.get('stock.accrual.wizard.line')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        res = []

        wzd_brw.line_ids.unlink()

        if wzd_brw.type == 'sale':
            res = self.compute_sale_lines(cr, uid, ids, context=context)
        elif wzd_brw.type == 'purchase':
            res = self.compute_purchase_lines(cr, uid, ids, context=context)
        for rex in res:
            # if not any([rex['debit'], rex['credit']]):
            #     continue
            sawl_obj.create(cr, uid, rex, context=context)

        return True

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)

        self.compute_lines(cr, uid, ids, context=context)

        datas = {'active_ids': ids}
        context['active_ids'] = ids
        context['active_model'] = 'stock.accrual.wizard'

        context['xls_report'] = wzd_brw.report_format == 'xls'
        name = 'stock_accrual_report.stock_accrual_report_name'
        return self.pool['report'].get_action(cr, uid, [], name, data=datas,
                                              context=context)
