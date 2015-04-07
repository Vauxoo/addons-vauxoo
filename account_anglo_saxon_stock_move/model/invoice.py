##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)
#    2004-2010 Tiny SPRL (<http://tiny.be>).
#    2009-2010 Veritos (http://veritos.nl).
#    All Rights Reserved
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

from openerp.osv import osv
from openerp import models, api


class AccountInvoice(osv.osv):
    _inherit = "account.invoice"

    def reconcile_stock_accrual(self, cr, uid, ids, context=None):
        aml_obj = self.pool['account.move.line']
        for inv_brw in self.browse(cr, uid, ids, context=context):
            for ail_brw in inv_brw.invoice_line:
                res = {}
                if ail_brw.move_id:
                    for brw in ail_brw.move_id.aml_ids:
                        if brw.account_id.reconcile:
                            if res.get(brw.account_id.id, False):
                                res[brw.account_id.id]['debit'] += brw.debit
                                res[brw.account_id.id]['credit'] += brw.credit
                                res[brw.account_id.id]['ids'].append(brw.id)
                            else:
                                res[brw.account_id.id] = {
                                    'debit': brw.debit,
                                    'credit': brw.credit,
                                    'ids': [brw.id],
                                }
                for key, val in res.iteritems():
                    if val['debit'] == val['credit']:
                        aml_obj.reconcile(cr, uid, val['ids'])
                    elif len(val['ids']) > 1:
                        aml_obj.reconcile_partial(cr, uid, val['ids'])

        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(AccountInvoice, self).invoice_validate(
            cr, uid, ids, context=context)
        self.reconcile_stock_accrual(cr, uid, ids, context=context)
        return res


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        if line.get('sm_id', False):
            res['sm_id'] = line['sm_id']
        return res


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _anglo_saxon_stock_move_lines(self, cr, uid, res, ttype='customer',
                                      context=None):
        ail_obj = self.pool.get('account.invoice.line')
        fp_obj = self.pool.get('account.fiscal.position')
        rex = []
        for line in res:
            if not line.get('invl_id', False):
                rex.append(line)
                continue

            ail_brw = ail_obj.browse(cr, uid, line['invl_id'], context=context)
            pp_brw = ail_brw.product_id
            if not (pp_brw and pp_brw.valuation == 'real_time' and
                    pp_brw.type != 'service'):
                rex.append(line)
                continue

            aa = None
            if ttype == 'supplier':
                oa = pp_brw.property_stock_account_input and \
                    pp_brw.property_stock_account_input.id or \
                    pp_brw.categ_id.property_stock_account_input_categ and\
                    pp_brw.categ_id.property_stock_account_input_categ.id
            elif ttype == 'customer':
                oa = pp_brw.property_stock_account_output and \
                    pp_brw.property_stock_account_output.id or \
                    pp_brw.categ_id.property_stock_account_output_categ and\
                    pp_brw.categ_id.property_stock_account_output_categ.id

            if oa:
                fpos = ail_brw.invoice_id.fiscal_position or False
                aa = fp_obj.map_account(cr, uid, fpos, oa)
            if aa == line['account_id'] and ail_brw.move_id:
                line['sm_id'] = ail_brw.move_id.id

            rex.append(line)
        return rex

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_line,
                    self).move_line_get(cr, uid, invoice_id, context=context)
        inv = self.pool.get('account.invoice').browse(
            cr, uid, invoice_id, context=context)
        if inv.type in ('out_invoice', 'out_refund'):
            res = self._anglo_saxon_stock_move_lines(
                cr, uid, res, ttype='customer', context=context)
        elif inv.type in ('in_invoice', 'in_refund'):
            res = self._anglo_saxon_stock_move_lines(
                cr, uid, res, ttype='supplier', context=context)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
