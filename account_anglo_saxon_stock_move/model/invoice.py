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
from openerp import models, api, _
from openerp.exceptions import ValidationError

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
        for inv in self.filtered(lambda inv: inv.move_id):
            amr_ids = inv.invoice_line.mapped('move_id.aml_ids.reconcile_id')
            amr_ids.unlink()
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def reconcile_stock_accrual(self):
        aml_obj = self.env['account.move.line']
        for inv_brw in self:
            # We just care about lines which have a stock_move.aml_ids related
            all_aml_ids = aml_obj
            aml_ids = inv_brw.invoice_line.mapped('move_id.aml_ids')

            # In order to keep every single line reconciled we will look for
            # all the lines related to a purchase/sale order
            all_aml_ids |= aml_ids.mapped('purchase_id.aml_ids')
            all_aml_ids |= aml_ids.mapped('sale_id.aml_ids')

            categ_ids = all_aml_ids.filtered(
                lambda m:
                m.product_id and
                not m.product_id.categ_id.property_stock_journal)
            if categ_ids:
                raise ValidationError(_(
                    'The Stock Journal is missing on following '
                    'product categories: %s' % (', '.join(
                        categ_ids.mapped('name')))
                ))

            res = {}
            # Only stack those that are fully reconciled
            amr_ids = all_aml_ids.mapped('reconcile_id')
            amr_ids.unlink()

            # Let's group all the Accrual lines by Purchase/Sale Order, Product
            # and Account
            for aml_brw in all_aml_ids.filtered('account_id.reconcile'):
                doc_brw = aml_brw.purchase_id or aml_brw.sale_id
                account_id = aml_brw.account_id.id
                product_id = aml_brw.product_id
                res.setdefault((doc_brw, account_id, product_id), aml_obj)
                res[(doc_brw, account_id, product_id)] |= aml_brw

            for (doc_brw, account_id, product_id), aml_ids in res.items():
                if not len(aml_ids) > 1:
                    continue
                journal_id = product_id.categ_id.property_stock_journal.id
                try:
                    aml_ids.reconcile_partial(
                        writeoff_period_id=inv_brw.period_id.id,
                        writeoff_journal_id=journal_id)
                except orm.except_orm:
                    message = (
                        "Reconciliation was not possible with "
                        "Journal Items [%(values)s]" % dict(
                            values=", ".join([str(idx) for idx in aml_ids])))
                    _logger.exception(message)

        return True


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
