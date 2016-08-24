# coding: utf-8
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

from openerp.osv import osv, orm
from openerp import models, api

import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if line.get('sm_id', False):
            res['sm_id'] = line['sm_id']
        return res

    @api.multi
    def action_cancel(self):
        aml_obj = self.env['account.move.line']
        aml_ids = []
        for inv in self:
            if not inv.move_id:
                continue
            for aml_brw in inv.move_id.line_id:
                # Unreconcile all non-receivable and non-payable lines
                if aml_brw.account_id.reconcile and aml_brw.account_id.type \
                        not in ('receivable', 'payable'):
                    aml_ids.append(aml_brw.id)
        if aml_ids:
            aml_obj._remove_move_reconcile(aml_ids)

        return super(AccountInvoice, self).action_cancel()

    def reconcile_stock_accrual(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        aml_obj = self.pool['account.move.line']
        amr_obj = self.pool['account.move.reconcile']
        for inv_brw in self.browse(cr, uid, ids, context=context):
            for ail_brw in inv_brw.invoice_line:
                ail_brw.refresh()
                if not ail_brw.move_id:
                    continue
                if ail_brw.move_id.product_id != ail_brw.product_id:
                    continue

                res = {}
                amr_ids = [
                    aml_brw1.reconcile_id.id or
                    aml_brw1.reconcile_partial_id.id
                    for aml_brw1 in ail_brw.move_id.aml_ids
                    if aml_brw1.reconcile_id or aml_brw1.reconcile_partial_id
                ]

                if amr_ids:
                    amr_ids = list(set(amr_ids))
                    amr_obj.unlink(cr, uid, amr_ids, context=context)

                ail_brw.refresh()
                aml_brws = [
                    aml_brw
                    for aml_brw in ail_brw.move_id.aml_ids
                    if aml_brw.product_id and
                    aml_brw.account_id.reconcile and
                    aml_brw.product_id == ail_brw.product_id
                ]

                for brw in aml_brws:
                    if res.get(brw.account_id.id, False):
                        res[brw.account_id.id].append(brw.id)
                    else:
                        res[brw.account_id.id] = [brw.id]

                for val in res.values():
                    if not len(val) > 1:
                        continue
                    try:
                        aml_obj.reconcile_partial(cr, uid, val,
                                                  context=context)
                    except orm.except_orm:
                        message = (
                            "Reconciliation was not possible with "
                            "Journal Items [%(values)s]" % dict(
                                values=", ".join([str(idx) for idx in val])))
                        _logger.exception(message)

        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(AccountInvoice, self).invoice_validate(
            cr, uid, ids, context=context)
        self.reconcile_stock_accrual(cr, uid, ids, context=context)
        return res


class AccountInvoiceLine(osv.osv):
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
        res = super(AccountInvoiceLine,
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
