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

from openerp.osv import orm
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

    def inv_line_characteristic_hashcode(self, invoice_line):
        """Including `sm_id` key as part of a hash in the invoice line will
        prevent lines form same products to be group if they do not share the
        same ail.move_id foreign_key"""
        res = super(AccountInvoice, self).inv_line_characteristic_hashcode(
            invoice_line)
        return "%s-%s" % (res, invoice_line.get('sm_id', 'False'))

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if line.get('sm_id', False):
            res['sm_id'] = line['sm_id']
        return res

    @api.multi
    def action_move_create(self):
        """ This super will add a new key into the context sending
        `novalidate=True` in order to avoid validation at Entry Lines creation.
        When this method is run at invoice validation (action_move_crate)
        it commissions the creation of Journal Entry Lines at
        https://goo.gl/2GWgNY
        `move = account_move.with_context(ctx_nolang).create(move_vals)`
        where each line created is validated at https://goo.gl/J2DQ13
        `tmp = move_obj.validate(cr, uid, [vals['move_id']], context)`
        after all lines are created and glued their Journal Entry is posted at
        https://goo.gl/8JbZpP `move.post()` which in turn does another
        validation on all the previous Journal Items at https://goo.gl/KHuwpR
        `valid_moves = self.validate(cr, uid, ids, context)`.
        Therefore, when creating the Journal Entry for an invoice it is enough
        to do one validate when posting the Journal Entry and skip the other
        validations at creation time

        """
        ctx = dict(self._context, novalidate=True)
        return \
            super(AccountInvoice, self.with_context(ctx)).action_move_create()

    @api.multi
    def action_cancel(self):
        aml_ids = self.mapped('move_id.line_id').filtered('sm_id')
        aml_ids.mapped('reconcile_id').unlink()
        return super(AccountInvoice, self).action_cancel()

    def _get_accrual_query(self, query_col, query_type, query_params):
        if query_type == 'query1':
            query = self._get_accrual_query1(query_col)
        elif query_type == 'query2':
            query = self._get_accrual_query2(query_col)
        elif query_type == 'query3':
            query = self._get_accrual_query3(query_col)
        elif query_type == 'query4':
            query = self._get_accrual_query4(query_col)
        else:
            raise ValidationError(
                _('This query has not yet being implemented: %s'), query_type)
        return self._cr.mogrify(query, query_params)

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
                HAVING COUNT(aml.id) > 1
                AND ABS(SUM(aml.debit - aml.credit)) <= %(offset)s
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

    def _get_accrual_query3(self, query_col):
        # /!\ ALERT: SQL INJECTION RISK
        query = '''
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
                AND state = 'valid'
                AND aml.company_id = %(company_id)s
                AND aa.reconcile = TRUE
            GROUP BY ''' + query_col + ''', product_id, account_id
            HAVING COUNT(aml.id)  > 1
            AND ABS(SUM(aml.debit - aml.credit)) <= %(offset)s -- Threashold
            ;'''

        return query

    def _get_accrual_query4(self, query_col):
        # In order to keep every single line reconciled we will look for all
        # the lines related to a purchase/sale order
        # /!\ ALERT: SQL INJECTION RISK
        query = '''
            SELECT
                aml.''' + query_col + ''',
                ARRAY_AGG(aml.id) as aml_ids
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                ''' + query_col + ''' IN %(ids)s
                AND reconcile_id IS NULL
                AND product_id IS NOT NULL
                AND state = 'valid'
                AND aml.company_id = %(company_id)s
                AND aa.reconcile = TRUE
            GROUP BY aml.''' + query_col + '''
            ;'''
        return query

    def _compute_query(self, ids, query_col, query_type):
        res = {}.fromkeys(ids, 0)
        company_id = self.env['res.users'].browse(self._uid).company_id
        query_params = {'ids': ids, 'offset': company_id.accrual_offset}
        query = self._get_accrual_query(query_col, query_type, query_params)
        self._cr.execute(query)
        res.update(dict(self._cr.fetchall()))
        return res

    def _compute_value(self, ids, name, query_type, query_col):
        if query_col == 'sale_id':
            obj = self.env['sale.order']
        elif query_col == 'purchase_id':
            obj = self.env['purchase.order']
        res = self._compute_query(ids, query_col, query_type)
        for brw in obj.browse(ids):
            brw[name] = res.get(brw.id, 0)

    def _compute_search(self, name, query_type, query_col, operator, value):
        if query_col == 'sale_id':
            obj = self.env['sale.order']
        elif query_col == 'purchase_id':
            obj = self.env['purchase.order']
        res = self._compute_query(obj.search([])._ids, query_col, query_type)
        ids = [rec_id
               for (rec_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]
        return [('id', 'in', ids)]

    @api.multi
    def cron_accrual_reconciliation(self, query_col, do_commit=False):
        if query_col == 'sale_id':
            ttype = 'Sale'
        elif query_col == 'purchase_id':
            ttype = 'Purchase'

        _logger.info('Reconciling %s Order Stock Accruals', ttype)
        company_id = self.env['res.users'].browse(self._uid).company_id
        query_params = {
            'offset': company_id.accrual_offset,
            'company_id': company_id.id}
        query = self._get_accrual_query(query_col, 'query3', query_params)
        self._cr.execute(query)
        ids = list(set(x[0] for x in self._cr.fetchall()))
        if not ids:
            _logger.info('None %s Order Stock Accruals to Reconcile', ttype)
            return
        self.env['account.invoice'].reconcile_stock_accrual(
            ids, query_col, do_commit=do_commit)
        _logger.info('Reconciling %s Order Stock Accruals Ended', ttype)

    @api.multi
    def reconcile_stock_accrual(self, rec_ids, query_col, do_commit=False):
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

        query_params = {'ids': tuple(rec_ids), 'company_id': company_id.id}
        query = self._get_accrual_query(query_col, 'query4', query_params)
        self._cr.execute(query)

        if query_col == 'sale_id':
            obj = self.env['sale.order']
        elif query_col == 'purchase_id':
            obj = self.env['purchase.order']

        msg = 'Reconciling account_id %s, product_id %s, no. items: %s'

        journal_ids = {}

        genexp = ((brw_id, ids) for brw_id, ids in self._cr.fetchall()
                  if len(ids) > 1)

        for brw_id, ids in genexp:
            fnc_post = obj.browse(brw_id).message_post
            count += 1
            _logger.info(
                'Attempting Reconciliation at %s:%s - %s/%s',
                query_col, brw_id, count, total)

            all_aml_ids = aml_obj.browse(ids)

            categ_ids = all_aml_ids.filtered(
                lambda m:
                not m.product_id.categ_id.property_stock_journal).mapped(
                    'product_id.categ_id')
            if categ_ids:
                raise ValidationError(
                    _('The Stock Journal is missing on following '
                      'product categories: %s'),
                    ', '.join(categ_ids.mapped('name'))
                )

            res = {}

            # Only stack those that are partially reconciled
            all_aml_ids.mapped('reconcile_partial_id').unlink()

            # Let's group all the Accrual lines by Purchase/Sale Order, Product
            # and Account
            for aml_brw in all_aml_ids:
                account_id = aml_brw.account_id.id
                product_id = aml_brw.product_id
                res.setdefault((account_id, product_id.id), aml_obj)
                res[(account_id, product_id.id)] |= aml_brw
                if product_id.id not in journal_ids:
                    journal_ids[product_id.id] = \
                        product_id.categ_id.property_stock_journal.id

            msg_log = []
            error_set = set()
            gen = (
                (account_id, product_id, aml_ids)
                for (account_id, product_id), aml_ids in res.items()
                if len(aml_ids) > 1)
            for account_id, product_id, aml_ids in gen:
                journal_id = journal_ids[product_id]
                writeoff_amount = sum(l.debit - l.credit for l in aml_ids)

                log = msg % (account_id, product_id, len(aml_ids))
                _logger.info(log)
                # /!\ NOTE: Reconcile with write off
                try:
                    rec_id = None
                    if ((writeoff and abs(writeoff_amount) <= offset) or
                            float_is_zero(
                                writeoff_amount, precision_digits=precision)):
                        rec_id = aml_ids.reconcile(
                            type='manual',
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                    # /!\ NOTE: I @hbto advise you to neglect the use of this
                    # option. AS it is resource wasteful and provide little
                    # value. Use only if you really find it Useful to
                    # partially reconcile loose lines
                    elif ((not writeoff and abs(writeoff_amount) <= offset) or
                            do_partial):
                        rec_id = aml_ids.reconcile_partial(
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                    if rec_id:
                        msg_log.append(log)
                except orm.except_orm, e:
                    if do_commit:
                        error_set.add((e.name, e.value, e.message))
                    else:
                        raise

            if msg_log:
                msg_log = '\n'.join(msg_log)
                fnc_post(
                    subject='Accruals Reconciled at %s' % time.ctime(),
                    body='Applying reconciliation on Order\n%s' % msg_log)

            if error_set:
                obj._cr.rollback()
                msg_log = '\n'.join('%s: %s %s' % lmg for lmg in error_set)
                fnc_post(
                    subject='Errors at reconciliation at %s' % time.ctime(),
                    body='Following errors were found\n%s' % msg_log)

            if do_commit:
                obj._cr.commit()

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


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _anglo_saxon_stock_move_lines(self, res, ttype='customer'):

        aa_res = {}
        for line in res:
            if 'invl_id' not in line:
                continue

            ail_brw = self.browse(line['invl_id'])
            pp_brw = ail_brw.product_id
            if (not pp_brw or pp_brw.valuation != 'real_time' or
                    pp_brw.type == 'service' or not ail_brw.move_id):
                continue

            if pp_brw.id not in aa_res:
                if ttype == 'supplier':
                    oa = pp_brw.property_stock_account_input or \
                        pp_brw.categ_id.property_stock_account_input_categ
                elif ttype == 'customer':
                    oa = pp_brw.property_stock_account_output or \
                        pp_brw.categ_id.property_stock_account_output_categ
                aa_res[pp_brw.id] = \
                    ail_brw.invoice_id.fiscal_position.map_account(oa)

            if aa_res[pp_brw.id].id == line['account_id']:
                line['sm_id'] = ail_brw.move_id.id

        return res

    @api.model
    def move_line_get(self, invoice_id):
        res = super(AccountInvoiceLine, self).move_line_get(invoice_id)
        inv = self.env['account.invoice'].browse(invoice_id)
        if inv.type in ('out_invoice', 'out_refund'):
            res = self._anglo_saxon_stock_move_lines(res, ttype='customer')
        elif inv.type in ('in_invoice', 'in_refund'):
            res = self._anglo_saxon_stock_move_lines(res, ttype='supplier')
        return res
