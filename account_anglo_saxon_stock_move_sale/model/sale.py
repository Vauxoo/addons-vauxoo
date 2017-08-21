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

from openerp.osv import orm
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.multi
    def _compute_accrual_reconciled(self):
        for po_brw in self:
            unreconciled_lines = len(po_brw.mapped('aml_ids').filtered(
                lambda l: l.account_id.reconcile and not l.reconcile_id))
            po_brw.accrual_reconciled = not bool(unreconciled_lines)
            po_brw.unreconciled_lines = unreconciled_lines

    accrual_reconciled = fields.Boolean(
        compute='_compute_accrual_reconciled',
        string="Reconciled Accrual",
        help="Indicates if All Accrual Journal Items are reconciled")
    unreconciled_lines = fields.Integer(
        compute='_compute_accrual_reconciled',
        string="Unreconciled Accrual Lines",
        help="Indicates how many Accrual Journal Items are unreconciled")
    aml_ids = fields.One2many(
        'account.move.line', 'sale_id', 'Account Move Lines',
        help='Journal Entry Lines related to this Sale Order')

    def cron_sale_accrual_reconciliation(
            self, cr, uid, writeoff=False, context=None):
        cr.execute('''
            SELECT
                aml.sale_id AS id
                , aml.product_id as product_id
                , aml.account_id as account_id
                , COUNT(aml.id) as count
                , SUM(aml.debit - aml.credit)
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
            ORDER BY count DESC, id DESC, product_id DESC
            ;
            ''', (2,))

        ids = list(set(x[0] for x in cr.fetchall()))
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

        writeoff = True  # TODO: Set on company
        accrual_offset = 2  # TODO: Set on company
        do_partial = False  # TODO: Set on company

        for po_brw in self:
            count += 1

            # In order to keep every single line reconciled we will look for
            # all the lines related to a purchase/sale order
            self._cr.execute('''
                SELECT
                    aml.id
                FROM account_move_line aml
                INNER JOIN account_account aa ON aa.id = aml.account_id
                WHERE
                    sale_id =%s
                    AND reconcile_id IS NULL
                    AND product_id IS NOT NULL
                    AND aa.reconcile = TRUE
                ;
                ''', (po_brw.id,))

            ids = [x[0] for x in self._cr.fetchall()]

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
                    if writeoff and abs(writeoff_amount) <= accrual_offset:
                        aml_ids.reconcile(
                            type='manual',
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                        do_commit = True
                        continue
                    elif abs(writeoff_amount) <= accrual_offset:
                        aml_ids.reconcile_partial(
                            writeoff_period_id=period_id,
                            writeoff_journal_id=journal_id)
                        do_commit = True
                        continue
                    # /!\ NOTE: I @hbto advise you to neglect the use of this
                    # option. AS it is resource wasteful and provide little
                    # value. Use only if you really find it Useful to
                    # partially reconcile loose lines
                    if do_partial:
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
                po_brw._cr.commit()

        return True

    def view_accrual(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        res = []
        for sale_brw in self.browse(cr, uid, ids, context=context):
            res += [aml_brw.id
                    for aml_brw in sale_brw.aml_ids
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
