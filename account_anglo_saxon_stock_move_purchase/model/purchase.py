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
from openerp.osv import orm
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    aml_ids = fields.One2many(
        'account.move.line', 'purchase_id', 'Account Move Lines',
        help='Journal Entry Lines related to this Purchase Order')

    @api.multi
    def reconcile_stock_accrual(self):
        aml_obj = self.env['account.move.line']
        ap_obj = self.env['account.period']
        date = fields.Date.context_today(self)
        period_id = ap_obj.with_context(self._context).find(date)[:1].id,
        for po_brw in self:

            # In order to keep every single line reconciled we will look for
            # all the lines related to a purchase/sale order
            all_aml_ids = po_brw.mapped('aml_ids')

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
                        writeoff_period_id=period_id,
                        writeoff_journal_id=journal_id)

                except orm.except_orm:
                    message = (
                        "Reconciliation was not possible with "
                        "Journal Items [%(values)s]" % dict(
                            values=", ".join([str(idx) for idx in aml_ids])))
                    _logger.exception(message)

        return True

    def view_accrual(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        res = []
        for purchase_brw in self.browse(cr, uid, ids, context=context):
            res += [aml_brw.id
                    for aml_brw in purchase_brw.aml_ids
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
