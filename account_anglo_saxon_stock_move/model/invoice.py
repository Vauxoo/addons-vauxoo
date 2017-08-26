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
import logging
import operator as py_operator
import time

from openerp.osv import osv, orm
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_is_zero

_logger = logging.getLogger(__name__)

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}


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

    def _get_accrual_query(self, query_col, query_type):
        if query_type == 'query1':
            query = self._get_accrual_query1(query_col)
        elif query_type == 'query2':
            query = self._get_accrual_query2(query_col)
        else:
            raise ValidationError(
                _('This query has not yet being implemented: %s'), query_type)
        return query

    def _get_accrual_query1(self, query_col):
        # /!\ ALERT: SQL INJECTION RISK
        query = '''
            SELECT ''' + query_col + ''', SUM(qty)
            FROM (
                SELECT
                    aml.''' + query_col + ''' AS ''' + query_col + ''',
                    aml.product_id as product_id,
                    aml.account_id as account_id,
                    COUNT(aml.id) as qty
                FROM account_move_line aml
                INNER JOIN account_account aa ON aa.id = aml.account_id
                WHERE
                    ''' + query_col + ''' IN %(ids)s
                    AND product_id IS NOT NULL
                    AND reconcile_id IS NULL
                    AND aa.reconcile = TRUE
                GROUP BY ''' + query_col + ''', product_id, account_id
                HAVING ABS(SUM(aml.debit - aml.credit)) <= %(offset)s
                ) AS view
            GROUP BY ''' + query_col + '''
            ;'''
        return query

    def _get_accrual_query2(self, query_col):
        # /!\ ALERT: SQL INJECTION RISK
        query = '''
            SELECT
                aml.''' + query_col + ''' AS ''' + query_col + ''',
                COUNT(aml.id) as qty
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                ''' + query_col + ''' IN %(ids)s
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY ''' + query_col + '''
            ;'''

        return query

    def _compute_query(self, ids, query_col, query_type):
        res = {}.fromkeys(ids, 0)
        company_id = self.env['res.users'].browse(self._uid).company_id
        query_params = {'ids': ids, 'offset': company_id.accrual_offset}
        query = self._get_accrual_query(query_col, query_type)
        self._cr.execute(query, query_params)
        res.update(dict(self._cr.fetchall()))
        return res

    def _compute_value(self, ids, name, query_type, query_col):
        if query_col == 'sale_id':
            obj = self.env['sale.order']
        elif query_col == 'purchase_id':
            obj = self.env['purchase.order']
        else:
            raise ValidationError(
                _('This field has not yet being implemented: %s'), query_col)
        res = self._compute_query(ids, query_col, query_type)
        for brw in obj.browse(ids):
            brw[name] = res.get(brw.id, 0)

    def _compute_search(self, name, query_type, query_col, operator, value):
        if query_col == 'sale_id':
            obj = self.env['sale.order']
        elif query_col == 'purchase_id':
            obj = self.env['purchase.order']
        else:
            raise ValidationError(
                _('This field has not yet being implemented: %s'), query_col)
        res = self._compute_query(obj.search([])._ids, query_col, query_type)
        ids = [rec_id
               for (rec_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]
        return [('id', 'in', ids)]

    @api.multi
    def cron_accrual_reconciliation(self, query_col):
        if query_col == 'sale_id':
            ttype = 'Sale'
        elif query_col == 'purchase_id':
            ttype = 'Purchase'
        else:
            raise ValidationError(
                _('This field has not yet being implemented: %s'), query_col)

        _logger.info('Reconciling %s Order Stock Accruals', ttype)
        company_id = self.env['res.users'].browse(self._uid).company_id
        # /!\ ALERT: SQL INJECTION RISK
        self._cr.execute('''
            SELECT
                aml.''' + query_col + ''' AS id,
                aml.product_id as product_id,
                aml.account_id as account_id,
                COUNT(aml.id) as count
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                ''' + query_col + ''' IS NOT NULL
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY ''' + query_col + ''', product_id, account_id
            HAVING COUNT(aml.id)  > 1
            AND ABS(SUM(aml.debit - aml.credit)) <= %s -- Use Threashold
            ;
            ''', (company_id.accrual_offset,))

        ids = list(set(x[0] for x in self._cr.fetchall()))
        if not ids:
            return
        self.env['account.invoice'].reconcile_stock_accrual(ids, query_col)
        _logger.info('Reconciling %s Order Stock Accruals Ended', ttype)

    @api.multi
    def reconcile_stock_accrual(self, rec_ids, query_col):
        if query_col == 'sale_id':
            obj = self.env['sale.order']
        elif query_col == 'purchase_id':
            obj = self.env['purchase.order']
        else:
            raise ValidationError(
                _('This field has not yet being implemented: %s'), query_col)

        aml_obj = self.env['account.move.line']
        ap_obj = self.env['account.period']
        date = fields.Date.context_today(self)
        period_id = ap_obj.with_context(self._context).find(date)[:1].id
        precision = self.env['decimal.precision'].precision_get('Account')

        total = len(rec_ids)
        count = 0

        company_id = self.env['res.users'].browse(self._uid).company_id
        writeoff = company_id.writeoff
        offset = company_id.accrual_offset
        do_partial = company_id.do_partial

        # In order to keep every single line reconciled we will look for all
        # the lines related to a purchase/sale order
        # /!\ ALERT: SQL INJECTION RISK
        query_params = {'ids': tuple(rec_ids)}

        query = []

        query.append('SELECT')
        query.append('aml.%s,' % query_col)
        query.append('''
                ARRAY_AGG(aml.id) as aml_ids
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE''')
        query.append('aml.%s' % query_col)
        query.append('''IN %(ids)s
                AND reconcile_id IS NULL
                AND product_id IS NOT NULL
                AND aa.reconcile = TRUE
            GROUP BY''')
        query.append('aml.%s' % query_col)
        query.append(';')

        query = ' '.join(query)
        query = self._cr.mogrify(query, query_params)
        self._cr.execute(query)

        for brw_id, ids in self._cr.fetchall():
            count += 1
            _logger.info(
                'Attempting Reconciliation at %s:%s - %s/%s',
                query_col, brw_id, count, total)

            if len(ids) < 2:
                continue

            all_aml_ids = aml_obj.browse(ids)

            categ_ids = all_aml_ids.filtered(
                lambda m:
                not m.product_id.categ_id.property_stock_journal).mapped(
                    'product_id.categ_id')
            if categ_ids:
                raise ValidationError(_(
                    'The Stock Journal is missing on following '
                    'product categories: %s' % (', '.join(
                        categ_ids.mapped('name')))
                ))

            res = {}

            # Only stack those that are partially reconciled
            all_aml_ids.mapped('reconcile_partial_id').unlink()

            # Let's group all the Accrual lines by Purchase/Sale Order, Product
            # and Account
            for aml_brw in all_aml_ids:
                account_id = aml_brw.account_id.id
                product_id = aml_brw.product_id
                res.setdefault((account_id, product_id), aml_obj)
                res[(account_id, product_id)] |= aml_brw

            do_commit = False
            for (account_id, product_id), aml_ids in res.items():
                if len(aml_ids) < 2:
                    continue
                journal_id = product_id.categ_id.property_stock_journal.id
                writeoff_amount = sum(l.debit - l.credit for l in aml_ids)
                try:
                    # /!\ NOTE: Reconcile with write off
                    if ((writeoff and abs(writeoff_amount) <= offset) or
                            float_is_zero(
                                writeoff_amount, precision_digits=precision)):
                        aml_ids.reconcile(
                            type='manual',
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                        do_commit = True
                    # /!\ NOTE: I @hbto advise you to neglect the use of this
                    # option. AS it is resource wasteful and provide little
                    # value. Use only if you really find it Useful to
                    # partially reconcile loose lines
                    elif ((not writeoff and abs(writeoff_amount) <= offset) or
                            do_partial):
                        aml_ids.reconcile_partial(
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                        do_commit = True

                except orm.except_orm:
                    message = (
                        "Reconciliation was not possible with "
                        "Journal Items [%(values)s]" % dict(
                            values=", ".join([str(idx) for idx in aml_ids])))
                    _logger.exception(message)

            if do_commit:
                obj.browse(brw_id).message_post(
                    subject='Accruals Reconciled at %s' % time.ctime(),
                    body='Applying reconciliation on Order')
                obj._cr.commit()
                _logger.info(
                    'Reconciling %s:%s - %s/%s',
                    query_col, brw_id, count, total)

    @api.multi
    def view_accrual(self, ids, model):
        brw = self.env[model].browse(ids)
        res = brw.aml_ids.filtered('account_id.reconcile')
        return {
            'domain':
            "[('id','in',[" + ','.join([str(item.id) for item in res]) + "])]",
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }


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
