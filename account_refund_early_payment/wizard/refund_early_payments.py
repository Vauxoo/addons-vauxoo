# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
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

from openerp import fields, api, models, osv
from openerp.tools import float_compare
# from openerp.tools.translate import _


class account_invoice_refund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    def _search_xml_id(self, cur, uid, model, record_xml_id, context=None):
        if context is None:
            context = {}
        imd_obj = self.pool.get('ir.model.data')
        res_id = False
        imd_id = imd_obj.search(cur, uid,
                                [('module', '=', model),
                                 ('name', '=', record_xml_id)])
        if imd_id:
            res_id = imd_obj.browse(cur, uid, imd_id)[0].res_id
        return res_id

    def _compute_amount(self, cur, uid, ids, field_names,
                        arg=None,
                        context=None,
                        query='', query_params=()):
        if context is None:
            context = {}
        res = {}
        for wzd in self.browse(cur, uid, ids, context=context):
            res[wzd.id] = wzd.percent * 10

        return res

    def default_get(self, cur, uid, fields_data, context=None):
        if context is None:
            context = {}
        ret = super(account_invoice_refund, self).default_get(cur, uid,
                                                              fields_data,
                                                              context=context)
        active_id = context.get('active_id', False)
        if active_id:
            ret['active_id'] = active_id
        return ret

    def onchange_amount_total(self, cur, uid, ids, percent=0.0,
                              active_id=None, context=None):
        if context is None:
            context = {}
        inv_obj = self.pool.get('account.invoice')
        inv = inv_obj.browse(cur, uid, active_id, context=context)
        return {
            'value': {
                'amount_total': inv.amount_total * (percent / 100),
            }
        }

    @api.model
    def _get_percent_default(self):
        """
        It is a hook method. In order to put some smart computation.
        """
        return 5.0

    filter_refund = fields.\
        Selection(selection_add=[('early_payment',
                                  'Early payment: Discount early payment')])
    percent = fields.Float('Percent', default=_get_percent_default)
    product_id = fields.Many2one('product.product', string='Product')
    amount_total = fields.Float('Amount')
    active_id = fields.Integer('Active ID')

    def compute_refund(self, cur, uid, ids, mode='refund', context=None):
        context = dict(context or {})

        result = super(account_invoice_refund, self).compute_refund(
            cur, uid, ids, mode, context=context)

        if mode != 'early_payment':
            return result

        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        account_m_line_obj = self.pool.get('account.move.line')

        refund_id = result.get('domain')[1][2]

        wizard_brw = self.browse(cur, uid, ids, context=context)
        # percent = wizard_brw.percent / 100.0
        amount_total = wizard_brw.amount_total
        prod_brw = wizard_brw.product_id

        # prec = self.pool.get('decimal.precision').precision_get(
        #     cur, uid, 'Account')
        for inv in inv_obj.browse(cur, uid, context.get('active_ids'),
                                  context=context):
            brw = inv_obj.browse(cur, uid, refund_id, context=context)

            if not brw.invoice_line:
                continue

            # if float_compare(amount_total, inv.amount_total * percent,
            #                  precision_digits=prec) > 0:
            #     raise osv.except_osv(
            #         _('Error!'),
            #         _("Make sure you have properly set Discounts, Discount "
            #           "is greater than allowed"))

            refund_line = brw.invoice_line[0]

            new_refund_line = inv_line_obj.copy_data(
                cur, uid, refund_line.id)
            new_refund_line['quantity'] = 1.0

            inv_line_obj.unlink(
                cur, uid, [rl.id for rl in brw.invoice_line])

            fp = inv.fiscal_position and inv.fiscal_position.id
            data = inv_line_obj.product_id_change(
                cur, uid, [],
                prod_brw.id,
                prod_brw.uom_id.id,
                1.0,
                prod_brw.name,
                inv.type,
                inv.partner_id.id,
                fp,
                amount_total,
                inv.currency_id.id,
                inv.company_id.id
                )

            if 'value' in data and data['value']:
                new_refund_line.update(data['value'])

            new_refund_line['price_unit'] = amount_total
            new_refund_line['product_id'] = prod_brw.id
            inv_line_obj.create(cur, uid, new_refund_line,
                                context=context)

            brw.button_reset_taxes()
            to_reconcile_ids = {}

            for line in inv.move_id.line_id:
                if line.account_id.reconcile and not line.reconcile_id:
                    to_reconcile_ids.setdefault(line.account_id.id,
                                                []).append(line.id)

            brw.signal_workflow('invoice_open')
            brw = inv_obj.browse(cur, uid, refund_id[0], context=context)

            for tmpline in brw.move_id.line_id:
                if tmpline.account_id.reconcile:
                    to_reconcile_ids[tmpline.
                                     account_id.id].append(tmpline.id)

            for account in to_reconcile_ids:
                if len(to_reconcile_ids[account]) > 1:
                    account_m_line_obj.reconcile_partial(
                        cur, uid, to_reconcile_ids[account],
                        context=context)

        return result

    _defaults = {
        'product_id': lambda self, cur,
        uid, c: self._search_xml_id(cur,
                                    uid,
                                    'account_refund_early_payment',
                                    'product_discount_early_payment',
                                    context=c),

    }
