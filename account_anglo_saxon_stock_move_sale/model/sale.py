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

_logger = logging.getLogger(__name__)

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}


class SaleOrder(models.Model):

    _inherit = "sale.order"
    query = '''
        SELECT sale_id, SUM(qty)
        FROM (
            SELECT
                aml.sale_id AS sale_id,
                aml.product_id as product_id,
                aml.account_id as account_id,
                COUNT(aml.id) as qty
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                sale_id IN %s
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY sale_id, product_id, account_id
            HAVING ABS(SUM(aml.debit - aml.credit)) <= %s -- Use Threashold
            ) AS view
        GROUP BY sale_id
        ;'''

    query2 = '''
        SELECT
            aml.sale_id AS sale_id,
            COUNT(aml.id) as qty
        FROM account_move_line aml
        INNER JOIN account_account aa ON aa.id = aml.account_id
        WHERE
            sale_id IN %s
            AND product_id IS NOT NULL
            AND reconcile_id IS NULL
            AND aa.reconcile = TRUE
        GROUP BY sale_id
        ;'''

    @api.multi
    def _compute_pending_reconciliation(self):

        company_id = self.env['res.users'].browse(self._uid).company_id
        offset = company_id.accrual_offset

        self._cr.execute(self.query, (tuple(self._ids), offset))
        res = dict(self._cr.fetchall())

        for brw in self:
            brw.reconciliation_pending = res.get(brw.id, 0)

        return

    def _search_pending_reconciliation(self, operator, value):
        ids = self.search([])._ids
        res = {}.fromkeys(ids, 0)
        company_id = self.env['res.users'].browse(self._uid).company_id
        offset = company_id.accrual_offset
        self._cr.execute(self.query, (tuple(ids), offset))

        res.update(dict(self._cr.fetchall()))

        ids = [sale_id
               for (sale_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]

        return [('id', 'in', ids)]

    @api.multi
    def _compute_unreconciled_lines(self):
        self._cr.execute(self.query2, (tuple(self._ids),))
        res = dict(self._cr.fetchall())
        for brw in self:
            brw.unreconciled_lines = res.get(brw.id, 0)
        return

    def _search_unreconciled_lines(self, operator, value):
        ids = self.search([])._ids
        res = {}.fromkeys(ids, 0)

        self._cr.execute(self.query2, (tuple(ids),))
        res.update(dict(self._cr.fetchall()))

        ids = [sale_id
               for (sale_id, computed_value) in res.items()
               if OPERATORS[operator](computed_value, value)]

        return [('id', 'in', ids)]

    unreconciled_lines = fields.Integer(
        compute='_compute_unreconciled_lines',
        search='_search_unreconciled_lines',
        help="Indicates how many unreconciled lines are still standing")
    reconciliation_pending = fields.Integer(
        compute='_compute_pending_reconciliation',
        search='_search_pending_reconciliation',
        help="Indicates how many possible reconciliations are pending")
    aml_ids = fields.One2many(
        'account.move.line', 'sale_id', 'Account Move Lines',
        help='Journal Entry Lines related to this Sale Order')

    def cron_sale_accrual_reconciliation(self, cr, uid, context=None):
        _logger.info('Reconciling Sales Order Stock Accruals')
        company_id = self.pool['res.users'].browse(cr, uid, uid).company_id
        cr.execute('''
            SELECT
                aml.sale_id AS id,
                aml.product_id as product_id,
                aml.account_id as account_id,
                COUNT(aml.id) as count
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                sale_id IS NOT NULL
                AND product_id IS NOT NULL
                AND reconcile_id IS NULL
                AND aa.reconcile = TRUE
            GROUP BY sale_id, product_id, account_id
            HAVING COUNT(aml.id)  > 1
            AND ABS(SUM(aml.debit - aml.credit)) <= %s -- Use Threashold
            ;
            ''', (company_id.accrual_offset,))

        ids = list(set(x[0] for x in cr.fetchall()))
        if not ids:
            return
        self.browse(cr, uid, ids, context=context).reconcile_stock_accrual()

        return

    @api.multi
    def reconcile_stock_accrual(self):
        aml_obj = self.env['account.move.line']
        ap_obj = self.env['account.period']
        date = fields.Date.context_today(self)
        period_id = ap_obj.with_context(self._context).find(date)[:1].id

        total = len(self)
        count = 0

        company_id = self.env['res.users'].browse(self._uid).company_id
        writeoff = company_id.writeoff
        offset = company_id.accrual_offset
        do_partial = company_id.do_partial

        # In order to keep every single line reconciled we will look for all
        # the lines related to a purchase/sale order
        self._cr.execute('''
            SELECT
                aml.sale_id,
                ARRAY_AGG(aml.id) as aml_ids
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            WHERE
                sale_id IN %s
                AND reconcile_id IS NULL
                AND product_id IS NOT NULL
                AND aa.reconcile = TRUE
            GROUP BY aml.sale_id
            ;
            ''', (tuple(self._ids),))

        res_aml = dict(self._cr.fetchall())
        for brw in self:
            count += 1

            ids = res_aml.get(brw.id, [])

            if len(ids) < 2:
                continue

            all_aml_ids = aml_obj.browse(ids)

            # /!\ NOTE: This does not return Product Categories
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
            # Only stack those that are fully reconciled
            # amr_ids = all_aml_ids.mapped('reconcile_id')
            all_aml_ids.mapped('reconcile_partial_id').unlink()

            # Let's group all the Accrual lines by Purchase/Sale Order, Product
            # and Account
            for aml_brw in all_aml_ids:
                doc_brw = aml_brw.sale_id
                account_id = aml_brw.account_id.id
                product_id = aml_brw.product_id
                res.setdefault((doc_brw, account_id, product_id), aml_obj)
                res[(doc_brw, account_id, product_id)] |= aml_brw

            do_commit = False
            for (doc_brw, account_id, product_id), aml_ids in res.items():
                if len(aml_ids) < 2:
                    continue
                journal_id = product_id.categ_id.property_stock_journal.id
                writeoff_amount = sum(l.debit - l.credit for l in aml_ids)
                try:
                    # /!\ NOTE: Reconcile with write off
                    if writeoff and abs(writeoff_amount) <= offset:
                        aml_ids.reconcile(
                            type='manual',
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                        do_commit = True
                        continue
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
                        continue

                except orm.except_orm:
                    message = (
                        "Reconciliation was not possible with "
                        "Journal Items [%(values)s]" % dict(
                            values=", ".join([str(idx) for idx in aml_ids])))
                    _logger.exception(message)

            if do_commit:
                brw.message_post(
                    subject='Accruals Reconciled at %s' % time.ctime(),
                    body='Applying reconciliation on Order')
                brw._cr.commit()
                _logger.info(
                    'Reconciling Sale Order id:%s - %s/%s',
                    brw.id, count, total)

        return True

    def view_accrual(self, cr, uid, ids, context=None):
        ids = [ids] if isinstance(ids, (int, long)) else ids
        context = context or {}
        res = []
        for brw in self.browse(cr, uid, ids, context=context):
            res += [aml_brw.id
                    for aml_brw in brw.aml_ids
                    # This shall be taken away when fixing domain in aml_ids
                    if aml_brw.account_id.reconcile
                    ]
        return {
            'domain': "[('id','in',\
                [" + ','.join([str(item) for item in res]) + "])]",
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
